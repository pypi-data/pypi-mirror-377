import asyncio
import hmac
import json
import logging
import time
from hashlib import sha256
from typing import Any, Dict, List

import httpx

from .database import Database
from .utils import json_dumps


log = logging.getLogger(__name__)


def sign_payload(secret: str, timestamp: str, body_bytes: bytes) -> str:
    msg = (timestamp + ".").encode("utf-8") + body_bytes
    return hmac.new(secret.encode("utf-8"), msg, sha256).hexdigest()


async def _post_with_retries(url: str, headers: Dict[str, str], body: Dict[str, Any], timeout: int = 5) -> None:
    """Post webhook with intelligent retry policy and proper error handling."""
    import random

    max_attempts = 3
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                resp = await client.post(url, headers=headers, content=json_dumps(body).encode("utf-8"))

                # Success: 2xx or client errors (don't retry 4xx)
                if 200 <= resp.status_code < 400:
                    log.info("Webhook delivered successfully", extra={
                        "event": "webhook_delivered",
                        "url": url,
                        "status_code": resp.status_code,
                        "attempt": attempt
                    })
                    return
                elif 400 <= resp.status_code < 500:
                    # Client errors - don't retry
                    log.warning("Webhook rejected (client error)", extra={
                        "event": "webhook_rejected",
                        "url": url,
                        "status_code": resp.status_code,
                        "response": resp.text[:200]
                    })
                    return
                else:
                    # 5xx server errors - retry
                    log.warning("Webhook server error (will retry)", extra={
                        "event": "webhook_server_error",
                        "url": url,
                        "status_code": resp.status_code,
                        "attempt": attempt,
                        "max_attempts": max_attempts
                    })

            except Exception as e:
                log.warning("Webhook network error (will retry)", extra={
                    "event": "webhook_network_error",
                    "url": url,
                    "error": str(e),
                    "attempt": attempt,
                    "max_attempts": max_attempts
                })

            # Exponential backoff with jitter
            if attempt < max_attempts:
                base_delay = 2 ** (attempt - 1)
                jitter = random.uniform(0.1, 0.5)  # 10-50% jitter
                delay = base_delay + jitter
                await asyncio.sleep(min(delay, 30))  # Cap at 30 seconds

        # All attempts failed
        log.error("Webhook delivery failed after all attempts", extra={
            "event": "webhook_failed",
            "url": url,
            "attempts": max_attempts
        })


async def dispatch_webhooks(db: Database, project_id: int, event_type: str, payload: Dict[str, Any], timeout: int = 5) -> None:
    webhooks = db.list_webhooks(project_id)
    if not webhooks:
        return
    ts = str(int(time.time()))
    tasks: List[asyncio.Task] = []
    body = {
        "type": event_type,
        "project_id": project_id,
        "timestamp": int(ts),
        "payload": payload,
    }
    body_bytes = json_dumps(body).encode("utf-8")
    for wh in webhooks:
        if not wh.get("active"):
            continue
        events = wh.get("events") or []
        if events and event_type not in events:
            continue
        signature = sign_payload(wh["secret"], ts, body_bytes)
        headers = {
            "Content-Type": "application/json",
            "X-ATC-Event": event_type,
            "X-ATC-Timestamp": ts,
            "X-ATC-Signature": signature,
        }
        tasks.append(asyncio.create_task(_post_with_retries(wh["url"], headers, body, timeout)))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
