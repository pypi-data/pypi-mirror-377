import asyncio
import logging
import os
import sys
from typing import Any, Dict

from .database import Database
from .tools import (
    ToolContext,
    create_project,
    find_or_create_project,
    get_agent_status,
    get_doc_chunk,
    get_project_activity,
    get_project_digest,
    get_project_summary,
    get_recent_messages,
    list_docs,
    list_doc_versions,
    list_projects,
    list_webhooks,
    register_doc,
    register_doc_url,
    register_webhook,
    release_floor,
    search_docs,
    search_messages,
    send_message,
    set_agent_status,
    take_floor,
    remove_webhook,
    upload_image,
    upload_image_base64,
)
from .utils import configure_logging


def _build_context() -> ToolContext:
    """Build tool context with comprehensive config validation and logging."""
    log = logging.getLogger(__name__)

    # Environment configuration with validation
    db_path = os.getenv("ATC_DB_PATH", os.path.join(os.getcwd(), "agent-team-chat-enhanced", "data.db"))
    image_dir = os.getenv("ATC_IMAGE_DIR", os.path.join(os.getcwd(), "agent-team-chat-enhanced", "images"))

    # Rate limiting config
    try:
        rate_capacity = int(os.getenv("ATC_RATE_LIMIT_CAPACITY", "5"))
        rate_interval = int(os.getenv("ATC_RATE_LIMIT_INTERVAL", "60"))
        global_rate_limit = int(os.getenv("ATC_GLOBAL_RATE_LIMIT", "60"))  # Global ceiling per minute
        if rate_capacity < 1 or rate_interval < 1 or global_rate_limit < 1:
            raise ValueError("Rate limits must be positive integers")
    except ValueError as e:
        log.error("Invalid rate limit configuration: %s", e)
        raise RuntimeError(f"Configuration error: {e}") from e

    # Message and image limits
    try:
        max_message_kb = int(os.getenv("ATC_MAX_MESSAGE_KB", "32"))
        max_image_mb = int(os.getenv("ATC_MAX_IMAGE_MB", "8"))
        if max_message_kb < 1 or max_image_mb < 1:
            raise ValueError("Size limits must be positive")
    except ValueError as e:
        log.error("Invalid size limit configuration: %s", e)
        raise RuntimeError(f"Configuration error: {e}") from e

    # Log configuration (no secrets)
    log.info("Agent Team Chat configuration", extra={
        "event": "startup_config",
        "db_path": db_path,
        "image_dir": image_dir,
        "rate_capacity": rate_capacity,
        "rate_interval_sec": rate_interval,
        "global_rate_limit_per_min": global_rate_limit,
        "max_message_kb": max_message_kb,
        "max_image_mb": max_image_mb,
        "python_version": ".".join(map(str, sys.version_info[:3])),
    })

    # Create directories with proper error handling
    try:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)
    except OSError as e:
        log.error("Failed to create directories: %s", e)
        raise RuntimeError(f"Directory creation failed: {e}") from e

    # Initialize database with error handling
    try:
        db = Database(db_path)
        log.info("Database initialized successfully", extra={
            "event": "database_ready",
            "db_path": db_path,
            "fts5_available": True
        })
    except Exception as e:
        log.error("Database initialization failed: %s", e)
        raise

    return ToolContext(
        db=db,
        image_dir=image_dir,
        rate_capacity=rate_capacity,
        rate_interval=rate_interval,
        global_rate_limit=global_rate_limit,
        max_message_kb=max_message_kb,
        max_image_mb=max_image_mb
    )


def main() -> None:
    json_logs = os.getenv("ATC_LOG_JSON", "false").lower() in {"1", "true", "yes"}
    configure_logging(json_mode=json_logs)
    ctx = _build_context()
    # Seed Agent Etiquette doc if missing
    try:
        if not ctx.db.list_doc_versions("Agent Etiquette"):
            etiquette_text = """
# Agent Team Chat Etiquette & Best Practices

## Core Principles
**DO NOT reply to every message!** Only respond when you have something NEW and VALUABLE to add.

## Before Acting (ALWAYS do this first)
1. **Call get_recent_messages()** - Sync with current conversation
2. **Call search_docs()** - Check if someone already answered your question
3. **Call list_projects()** - Find existing chats before creating new ones

## When to Reply (Only if TRUE)
✅ You have NEW information that others don't
✅ You can solve a specific problem being discussed
✅ You're directly asked a question
✅ You can provide missing context or clarification
✅ You're the specialist for this topic

## When NOT to Reply (Never do these)
❌ Just to acknowledge or say "great job"
❌ To repeat what someone else already said
❌ To ask questions already answered in docs
❌ When the conversation has naturally concluded
❌ To provide generic advice without specifics

## Message Quality Guidelines
- **Be specific and actionable** - Include file paths, line numbers, exact commands
- **Provide evidence** - Link to docs, show code examples, cite sources
- **One main point per message** - Don't ramble or combine unrelated topics
- **Use upload_image() for visuals** - Screenshots, diagrams, code snippets
- **Respect rate limits** - Wait for retry_after if rate limited

## Project Management
- **Search existing projects first** with list_projects() before creating new ones
- **Use descriptive names** like "Bug Fix: Auth Token Validation" not "chat 1"
- **Join relevant existing chats** rather than creating duplicates
- **Set clear status** with set_agent_status() when working on something

## Coordination
- **Use floor control** for important announcements: take_floor() → speak → release_floor()
- **Check agent status** before expecting responses from specific agents
- **Be patient** - Other agents may be working on different timezones or priorities

## Emergency Protocol
If you see "urgent" or "emergency" in messages:
1. Take floor immediately if needed
2. Provide specific help, not general advice
3. Escalate to humans if beyond your capabilities

## Examples of Good vs Bad Responses

### ❌ BAD (Don't do this):
- "Great idea!"
- "I agree with what John said"
- "Thanks for sharing"
- "Looking into this now"

### ✅ GOOD (Do this):
- "Found the bug in auth.py:line 147 - the token validation is missing a null check. Here's the fix: [code]"
- "The API docs in our system show this was already solved in v2.3: [search result link]"
- "I've implemented the OAuth flow. Screenshot attached showing the working login form."

Remember: **Silence is often better than noise. Quality over quantity.**
"""
            register_doc(ctx, title="Agent Etiquette", text=etiquette_text, source="seed")
    except Exception:
        pass

    # Lazy import MCP and register tools
    try:
        import mcp
        from mcp.server import Server
    except Exception as e:  # pragma: no cover
        logging.getLogger(__name__).error(
            "MCP library not available: %s. Install Python 3.11+ and `pip install mcp`.\n"
            "You can still use the modules directly or run tests.",
            e,
        )
        return

    server = Server("agent-team-chat")

    # Register all tools with proper MCP handlers
    @server.call_tool()
    async def handle_tool_call(name: str, arguments: dict) -> Dict[str, Any]:
        """Handle all tool calls through a single dispatcher."""
        tool_map = {
            # Chat tools
            "create_project": create_project,
            "find_or_create_project": find_or_create_project,
            "list_projects": list_projects,
            "get_project_activity": get_project_activity,
            "send_message": send_message,
            "get_recent_messages": get_recent_messages,
            "search_messages": search_messages,
            "upload_image": upload_image,
            "upload_image_base64": upload_image_base64,
            "get_project_summary": get_project_summary,

            # Coordination tools
            "set_agent_status": set_agent_status,
            "get_agent_status": get_agent_status,
            "take_floor": take_floor,
            "release_floor": release_floor,
            "get_project_digest": get_project_digest,

            # Webhook tools
            "register_webhook": register_webhook,
            "list_webhooks": list_webhooks,
            "remove_webhook": remove_webhook,

            # Documentation tools
            "list_docs": list_docs,
            "search_docs": search_docs,
            "get_doc_chunk": get_doc_chunk,
            "register_doc": register_doc,
            "register_doc_url": register_doc_url,
            "list_doc_versions": list_doc_versions,
        }

        if name not in tool_map:
            return {"success": False, "error": {"code": "UNKNOWN_TOOL", "message": f"Unknown tool: {name}"}}

        try:
            func = tool_map[name]
            if asyncio.iscoroutinefunction(func):
                return await func(ctx, **arguments)
            else:
                return func(ctx, **arguments)
        except Exception as ex:
            return {"success": False, "error": {"code": "SERVER_ERROR", "message": str(ex)}}

    import mcp.server.stdio

    async def run_server():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    # Check if we should run the server or return it for testing
    if __name__ == "__main__":
        asyncio.run(run_server())
    else:
        # For use as a module, run the server
        asyncio.run(run_server())


if __name__ == "__main__":
    main()
