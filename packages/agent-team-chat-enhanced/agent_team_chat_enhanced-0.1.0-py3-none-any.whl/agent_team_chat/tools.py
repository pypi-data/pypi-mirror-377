import asyncio
import os
import shutil
from typing import Any, Dict, List, Optional

from .database import Database
from .events import dispatch_webhooks
from .rate_limiter import RateLimiter
from .utils import (
    AppError,
    decode_base64_data,
    epoch_ms,
    json_dumps,
    safe_filename,
    validate_image_file,
    write_bytes,
)
from . import docs as docs_mod


def ok(data: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"success": True, **(data or {})}


def err(code: str, message: str, retry_after: Optional[float] = None) -> Dict[str, Any]:
    e = {"code": code, "message": message}
    if retry_after is not None:
        e["retry_after"] = retry_after
    return {"success": False, "error": e}


class ToolContext:
    def __init__(self, db: Database, image_dir: str, rate_capacity: int = 5, rate_interval: int = 60,
                 global_rate_limit: int = 60, max_message_kb: int = 32, max_image_mb: int = 8):
        self.db = db
        self.image_dir = image_dir
        self.rate_limiter = RateLimiter(db, capacity=rate_capacity, interval_seconds=rate_interval, global_limit_per_min=global_rate_limit)
        self.global_rate_limit = global_rate_limit  # Per minute global ceiling
        self.max_message_bytes = max_message_kb * 1024
        self.max_image_bytes = max_image_mb * 1024 * 1024


# Chat tools
def create_project(ctx: ToolContext, name: str, description: Optional[str] = None) -> Dict:
    if not name or not name.strip():
        return err("INVALID_REQUEST", "name is required")
    try:
        pid = ctx.db.create_project(name.strip(), description or "")
        return ok({"project_id": pid})
    except Exception as e:
        return err("SERVER_ERROR", str(e))


def list_projects(ctx: ToolContext, limit: int = 50, offset: int = 0, search: Optional[str] = None) -> Dict:
    """List projects with optional search functionality."""
    projects = ctx.db.list_projects(limit=limit, offset=offset)

    # If search term provided, filter projects
    if search:
        search_lower = search.lower()
        filtered_projects = []
        for project in projects:
            name_match = search_lower in project["name"].lower()
            desc_match = search_lower in (project.get("description", "") or "").lower()
            if name_match or desc_match:
                filtered_projects.append(project)
        projects = filtered_projects

    return ok({"projects": projects, "search": search, "total": len(projects)})


def find_or_create_project(ctx: ToolContext, name: str, description: Optional[str] = None) -> Dict:
    """
    Smart project finder: searches for existing projects first, creates only if needed.
    This prevents agents from creating duplicate chats.
    """
    if not name or not name.strip():
        return err("INVALID_REQUEST", "name is required")

    name = name.strip()

    # First, search for existing projects with similar names
    search_result = list_projects(ctx, search=name, limit=20)
    if search_result["success"] and search_result["projects"]:
        # Found existing projects, return the best match
        projects = search_result["projects"]

        # Look for exact match first
        for project in projects:
            if project["name"].lower() == name.lower():
                return ok({
                    "project_id": project["id"],
                    "name": project["name"],
                    "description": project["description"],
                    "action": "found_exact_match",
                    "message": f"Found existing project: '{project['name']}'"
                })

        # If no exact match, suggest the closest matches
        suggestions = [{"id": p["id"], "name": p["name"], "description": p["description"]}
                      for p in projects[:3]]

        return ok({
            "action": "found_similar",
            "suggestions": suggestions,
            "message": f"Found {len(suggestions)} similar projects. Consider joining one of these instead of creating a new one.",
            "create_anyway": f"To create a new project anyway, use create_project(name='{name}', description='{description or ''}')"
        })

    # No similar projects found, create new one
    result = create_project(ctx, name=name, description=description)
    if result["success"]:
        result.update({
            "action": "created_new",
            "message": f"No similar projects found. Created new project: '{name}'"
        })

    return result


def get_project_activity(ctx: ToolContext, project_id: int, hours: int = 24) -> Dict:
    """Get recent activity summary for a project to help agents understand current context."""
    try:
        # Get recent messages
        messages = ctx.db.get_recent_messages(project_id=project_id, limit=50)

        if not messages:
            return ok({
                "project_id": project_id,
                "activity": "empty",
                "message": "No messages in this project yet",
                "recent_messages": 0,
                "active_agents": [],
                "last_activity": None
            })

        # Analyze activity
        now = epoch_ms()
        cutoff_time = now - (hours * 60 * 60 * 1000)  # Convert hours to milliseconds

        recent_messages = [msg for msg in messages if msg["created_at"] >= cutoff_time]
        all_agents = list(set(msg["agent"] for msg in messages))
        recent_agents = list(set(msg["agent"] for msg in recent_messages))

        # Get last message info
        last_message = messages[0] if messages else None

        # Determine activity level
        activity_level = "quiet"
        if len(recent_messages) > 20:
            activity_level = "very_active"
        elif len(recent_messages) > 10:
            activity_level = "active"
        elif len(recent_messages) > 3:
            activity_level = "moderate"
        elif len(recent_messages) > 0:
            activity_level = "light"

        return ok({
            "project_id": project_id,
            "activity": activity_level,
            "recent_messages": len(recent_messages),
            "total_messages": len(messages),
            "active_agents": recent_agents,
            "all_agents": all_agents,
            "last_activity": last_message["created_at"] if last_message else None,
            "last_agent": last_message["agent"] if last_message else None,
            "hours_analyzed": hours,
            "context_preview": messages[0]["content"][:200] + "..." if messages and len(messages[0]["content"]) > 200 else messages[0]["content"] if messages else None
        })

    except Exception as e:
        return err("SERVER_ERROR", str(e))


async def _dispatch_async(db: Database, project_id: int, event_type: str, payload: Dict[str, Any]):
    await dispatch_webhooks(db, project_id, event_type, payload)


def send_message(
    ctx: ToolContext,
    project_id: int,
    agent: str,
    role: str,
    content: str,
    image_path: Optional[str] = None,
) -> Dict:
    if not content or not role or not agent:
        return err("INVALID_REQUEST", "agent, role, content are required")
    allowed_roles = {"user", "assistant", "system", "tool"}
    if role not in allowed_roles:
        return err("INVALID_REQUEST", f"role must be one of {sorted(allowed_roles)}")

    # Enforce message length limits
    content_bytes = len(content.encode('utf-8'))
    if content_bytes > ctx.max_message_bytes:
        return err("MESSAGE_TOO_LARGE",
                  f"Message exceeds {ctx.max_message_bytes//1024}KB limit. "
                  f"Consider using upload_image() or upload_image_base64() for large content. "
                  f"Current size: {content_bytes//1024}KB")

    ok_rl, retry_after = ctx.rate_limiter.check_and_consume(agent=agent, project_id=project_id, cost=1)
    if not ok_rl:
        return err("RATE_LIMITED", "rate limit exceeded", retry_after=retry_after)

    # Truncate content if it's very close to limit (defensive)
    if content_bytes > ctx.max_message_bytes * 0.95:
        content = content[:ctx.max_message_bytes//2] + "... [truncated due to size]"

    msg_id = ctx.db.add_message(project_id=project_id, agent=agent, role=role, content=content, image_path=image_path)

    # Fire and forget dispatch
    try:
        asyncio.get_event_loop().create_task(_dispatch_async(ctx.db, project_id, "message.created", {
            "message_id": msg_id,
            "agent": agent,
            "role": role,
            "content": content,
            "image_path": image_path,
        }))
    except RuntimeError:
        # No loop running (e.g., sync env); run inline
        asyncio.run(_dispatch_async(ctx.db, project_id, "message.created", {
            "message_id": msg_id,
            "agent": agent,
            "role": role,
            "content": content,
            "image_path": image_path,
        }))
    return ok({"message_id": msg_id})


def get_recent_messages(ctx: ToolContext, project_id: int, limit: int = 50, before_id: Optional[int] = None) -> Dict:
    msgs = ctx.db.get_recent_messages(project_id=project_id, limit=limit, before_id=before_id)
    return ok({"messages": msgs})


def search_messages(ctx: ToolContext, project_id: int, query: str, limit: int = 50, offset: int = 0) -> Dict:
    msgs = ctx.db.search_messages(project_id=project_id, query=query, limit=limit, offset=offset)
    return ok({"messages": msgs})


# Image handling
def upload_image(ctx: ToolContext, path: str) -> Dict:
    if not os.path.exists(path):
        return err("INVALID_REQUEST", "file not found")
    valid, mime, reason = validate_image_file(path)
    if not valid:
        message = {
            "file_not_found": "file not found",
            "too_large": "image exceeds 8MB",
            "unsupported_type": "unsupported image type",
        }.get(reason or "", "invalid image")
        return err("INVALID_REQUEST", message)
    filename = safe_filename(os.path.basename(path))
    dest_path = os.path.join(ctx.image_dir, filename)
    os.makedirs(ctx.image_dir, exist_ok=True)
    shutil.copy2(path, dest_path)
    return ok({"image_path": dest_path, "mime": mime})


def upload_image_base64(ctx: ToolContext, base64_data: str, filename_hint: Optional[str] = None) -> Dict:
    try:
        data = decode_base64_data(base64_data)
    except Exception:
        return err("INVALID_REQUEST", "invalid base64 data")
    if len(data) > 8 * 1024 * 1024:
        return err("INVALID_REQUEST", "image exceeds 8MB")
    # Write temp then validate
    tmp_path = write_bytes(ctx.image_dir, filename_hint or "upload.bin", data)
    valid, mime, reason = validate_image_file(tmp_path)
    if not valid:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        message = {
            "too_large": "image exceeds 8MB",
            "unsupported_type": "unsupported image type",
        }.get(reason or "", "invalid image")
        return err("INVALID_REQUEST", message)
    return ok({"image_path": tmp_path, "mime": mime})


def get_project_summary(ctx: ToolContext, project_id: int, limit: int = 50) -> Dict:
    msgs = list(reversed(ctx.db.get_recent_messages(project_id=project_id, limit=limit)))
    # Simple heuristic: concatenate first sentence of each
    summary_parts: List[str] = []
    for m in msgs:
        text = (m.get("content") or "").strip()
        if not text:
            continue
        first = text.split(". ")[0]
        summary_parts.append(first[:160])
    summary = "; ".join(summary_parts)[:1000]
    return ok({"summary": summary})


# Coordination
def set_agent_status(ctx: ToolContext, project_id: Optional[int], agent: str, status: str, details: Optional[Dict[str, Any]] = None) -> Dict:
    now = epoch_ms()
    ctx.db.upsert_agent_status(agent=agent, project_id=project_id, status=status, details=details, last_seen=now, rate_tokens=None, rate_refill_ts=None)
    # Dispatch webhook
    payload = {"agent": agent, "status": status, "details": details or {}, "last_seen": now}
    try:
        asyncio.get_event_loop().create_task(_dispatch_async(ctx.db, project_id or 0, "status.updated", payload))
    except RuntimeError:
        asyncio.run(_dispatch_async(ctx.db, project_id or 0, "status.updated", payload))
    return ok({"agent": agent, "status": status, "details": details or {}, "last_seen": now})


def get_agent_status(ctx: ToolContext, project_id: Optional[int], agent: str) -> Dict:
    st = ctx.db.get_agent_status(agent=agent, project_id=project_id)
    if not st:
        return ok({"status": None})
    return ok({"status": st})


def take_floor(ctx: ToolContext, project_id: int, agent: str, ttl_seconds: int = 60) -> Dict:
    ok_take = ctx.db.take_floor(project_id=project_id, agent=agent, ttl_seconds=ttl_seconds)
    if not ok_take:
        fl = ctx.db.get_floor(project_id)
        holder = fl.get("holder_agent") if fl else None
        return err("FLOOR_HELD", f"floor is held by {holder}")
    payload = {"agent": agent, "ttl_seconds": ttl_seconds}
    try:
        asyncio.get_event_loop().create_task(_dispatch_async(ctx.db, project_id, "floor.taken", payload))
    except RuntimeError:
        asyncio.run(_dispatch_async(ctx.db, project_id, "floor.taken", payload))
    return ok({"holder": agent, "expires_at": ctx.db.get_floor(project_id).get("expires_at")})


def release_floor(ctx: ToolContext, project_id: int, agent: str) -> Dict:
    ok_rel = ctx.db.release_floor(project_id=project_id, agent=agent)
    if not ok_rel:
        return err("NOT_HELD", "agent does not hold floor")
    try:
        asyncio.get_event_loop().create_task(_dispatch_async(ctx.db, project_id, "floor.released", {"agent": agent}))
    except RuntimeError:
        asyncio.run(_dispatch_async(ctx.db, project_id, "floor.released", {"agent": agent}))
    return ok({"released": True})


def get_project_digest(ctx: ToolContext, project_id: int, recent: int = 50) -> Dict:
    # Build a naive digest from recent messages and store versioned digest
    msgs = list(reversed(ctx.db.get_recent_messages(project_id=project_id, limit=recent)))
    lines = []
    for m in msgs:
        agent = m.get("agent")
        role = m.get("role")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        lines.append(f"[{role}:{agent}] {content[:200]}")
    digest = "\n".join(lines)
    ctx.db.upsert_digest(project_id=project_id, content=digest)
    d = ctx.db.get_digest(project_id)
    return ok({"digest": d})


# Webhooks
def register_webhook(ctx: ToolContext, project_id: int, url: str, secret: str, events: Optional[List[str]] = None) -> Dict:
    try:
        wid = ctx.db.register_webhook(project_id=project_id, url=url, secret=secret, events=events or [])
        return ok({"webhook_id": wid})
    except Exception as e:
        return err("SERVER_ERROR", str(e))


def list_webhooks(ctx: ToolContext, project_id: int) -> Dict:
    return ok({"webhooks": ctx.db.list_webhooks(project_id=project_id)})


def remove_webhook(ctx: ToolContext, webhook_id: int) -> Dict:
    removed = ctx.db.remove_webhook(webhook_id)
    if not removed:
        return err("NOT_FOUND", "webhook not found")
    return ok({"removed": True})


# Docs
def list_docs(ctx: ToolContext, project_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> Dict:
    return ok({"docs": ctx.db.list_docs(project_id=project_id, limit=limit, offset=offset)})


def list_doc_versions(ctx: ToolContext, title: str) -> Dict:
    return ok({"versions": ctx.db.list_doc_versions(title=title)})


def search_docs(ctx: ToolContext, query: str, limit: int = 20, offset: int = 0) -> Dict:
    return ok({"results": docs_mod.search_docs(ctx.db, query=query, limit=limit, offset=offset)})


def get_doc_chunk(ctx: ToolContext, doc_id: int, chunk_index: int) -> Dict:
    chunk = docs_mod.get_doc_chunk(ctx.db, doc_id=doc_id, chunk_index=chunk_index)
    if not chunk:
        return err("NOT_FOUND", "chunk not found")
    return ok({"chunk": chunk})


def register_doc(ctx: ToolContext, title: str, text: str, source: Optional[str] = None, project_id: Optional[int] = None) -> Dict:
    res = docs_mod.register_doc(ctx.db, title=title, text=text, source=source, project_id=project_id)
    return ok(res)


def register_doc_url(ctx: ToolContext, url: str, title: Optional[str] = None, project_id: Optional[int] = None) -> Dict:
    res = docs_mod.register_doc_url(ctx.db, url=url, title=title, project_id=project_id)
    return ok(res)
