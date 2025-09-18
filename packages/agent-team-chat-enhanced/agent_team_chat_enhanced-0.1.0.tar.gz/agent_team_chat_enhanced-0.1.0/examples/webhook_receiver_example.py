#!/usr/bin/env python3
"""
Webhook Receiver Example

This script demonstrates how to receive and validate webhook notifications
from the Agent Team Chat MCP server. It includes HMAC signature verification
and example handling for different event types.

Run this script to start a webhook receiver server, then register this URL
with the Agent Team Chat system to receive notifications.
"""

import hashlib
import hmac
import json
import time
import sys
import os
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = FastAPI(title="Agent Team Chat Webhook Receiver")

# Store received events for demonstration
received_events = []

# This should match the secret you use when registering the webhook
WEBHOOK_SECRET = "your-webhook-secret-key"


def verify_signature(timestamp: str, body: bytes, received_signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature from Agent Team Chat webhook."""
    # Create the message that was signed: "{timestamp}." + body
    message = f"{timestamp}.".encode('utf-8') + body

    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        message,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures (use hmac.compare_digest for timing-safe comparison)
    return hmac.compare_digest(expected_signature, received_signature)


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive and process webhook from Agent Team Chat."""
    # Get headers
    timestamp = request.headers.get("X-ATC-Timestamp")
    signature = request.headers.get("X-ATC-Signature")
    event_type = request.headers.get("X-ATC-Event")

    if not timestamp or not signature or not event_type:
        raise HTTPException(status_code=400, detail="Missing required headers")

    # Read body
    body = await request.body()

    # Verify signature
    if not verify_signature(timestamp, body, signature, WEBHOOK_SECRET):
        print(f"❌ Invalid signature for event {event_type}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Check timestamp with clock skew tolerance (±5 minutes)
    now = int(time.time())
    webhook_time = int(timestamp)
    time_diff = abs(now - webhook_time)
    if time_diff > 300:  # 5 minutes tolerance
        print(f"❌ Webhook timestamp outside tolerance: {time_diff}s (max 300s)")
        print(f"   Server time: {now}, Webhook time: {webhook_time}")
        raise HTTPException(status_code=400, detail=f"Timestamp outside tolerance: {time_diff}s")

    # Parse JSON payload
    try:
        payload = json.loads(body.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Store event for demonstration
    event = {
        "event_type": event_type,
        "timestamp": webhook_time,
        "payload": payload,
        "received_at": time.time()
    }
    received_events.append(event)

    # Process different event types
    await process_event(event_type, payload)

    print(f"✅ Processed webhook: {event_type}")
    return {"status": "ok", "processed": True}


async def process_event(event_type: str, payload: Dict[str, Any]):
    """Process different types of events from Agent Team Chat."""

    if event_type == "message.created":
        await handle_message_created(payload)
    elif event_type == "image.uploaded":
        await handle_image_uploaded(payload)
    elif event_type == "status.updated":
        await handle_status_updated(payload)
    elif event_type == "floor.taken":
        await handle_floor_taken(payload)
    elif event_type == "floor.released":
        await handle_floor_released(payload)
    elif event_type.startswith("keyword:"):
        await handle_keyword_event(event_type, payload)
    else:
        print(f"⚠️ Unknown event type: {event_type}")


async def handle_message_created(payload: Dict[str, Any]):
    """Handle new message events."""
    agent = payload.get("agent", "Unknown")
    role = payload.get("role", "unknown")
    content = payload.get("content", "")

    print(f"💬 New message from {agent} ({role}): {content[:100]}...")

    # Example: Alert on urgent messages
    if "urgent" in content.lower() or "emergency" in content.lower():
        print(f"🚨 URGENT MESSAGE DETECTED from {agent}")
        # Here you could send alerts, notifications, etc.

    # Example: Track agent activity
    print(f"📊 Agent {agent} is active (message #{payload.get('message_id')})")


async def handle_image_uploaded(payload: Dict[str, Any]):
    """Handle image upload events."""
    agent = payload.get("agent", "Unknown")
    image_path = payload.get("image_path", "")

    print(f"🖼️ Image uploaded by {agent}: {image_path}")

    # Example: Process images for analysis
    # You could integrate with image recognition APIs, save to cloud storage, etc.


async def handle_status_updated(payload: Dict[str, Any]):
    """Handle agent status changes."""
    agent = payload.get("agent", "Unknown")
    status = payload.get("status", "unknown")
    details = payload.get("details", {})

    print(f"📍 {agent} status: {status}")
    if details:
        print(f"   Details: {details}")

    # Example: Alert when agents go offline
    if status in ["away", "offline"]:
        print(f"⚠️ Agent {agent} is now {status}")


async def handle_floor_taken(payload: Dict[str, Any]):
    """Handle floor control events."""
    agent = payload.get("agent", "Unknown")
    ttl = payload.get("ttl_seconds", 60)

    print(f"🎤 {agent} has taken the floor for {ttl} seconds")

    # Example: Track speaking time, enforce time limits, etc.


async def handle_floor_released(payload: Dict[str, Any]):
    """Handle floor release events."""
    agent = payload.get("agent", "Unknown")

    print(f"🎤 {agent} has released the floor")


async def handle_keyword_event(event_type: str, payload: Dict[str, Any]):
    """Handle keyword-based events (e.g., 'keyword:help', 'keyword:error')."""
    keyword = event_type.split(":", 1)[1] if ":" in event_type else "unknown"
    agent = payload.get("agent", "Unknown")

    print(f"🔔 Keyword '{keyword}' detected from {agent}")

    if keyword == "help":
        print(f"🆘 Help request from {agent} - routing to support team")
    elif keyword == "error":
        print(f"❌ Error reported by {agent} - investigating")


@app.get("/events")
async def get_events():
    """Get all received events (for debugging/monitoring)."""
    return {
        "total_events": len(received_events),
        "events": received_events[-10:]  # Return last 10 events
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "uptime": time.time(),
        "events_received": len(received_events)
    }


def main():
    """Start the webhook receiver server."""
    print("🎣 Agent Team Chat Webhook Receiver")
    print("=" * 50)
    print(f"🔐 Using webhook secret: {WEBHOOK_SECRET}")
    print("📡 Starting server on http://127.0.0.1:8080")
    print("💡 Register this URL with Agent Team Chat:")
    print("   URL: http://127.0.0.1:8080/webhook")
    print("   Secret: your-webhook-secret-key")
    print("   Events: ['message.created', 'status.updated', 'floor.taken']")
    print("")
    print("🔍 Monitor events at: http://127.0.0.1:8080/events")
    print("❤️ Health check at: http://127.0.0.1:8080/health")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")


if __name__ == "__main__":
    main()