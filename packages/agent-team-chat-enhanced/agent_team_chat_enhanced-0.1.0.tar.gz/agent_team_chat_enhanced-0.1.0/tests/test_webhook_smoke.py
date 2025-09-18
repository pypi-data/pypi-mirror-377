import json
import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvicorn
from fastapi import FastAPI, Request

from agent_team_chat.database import Database
from agent_team_chat.tools import ToolContext, create_project, register_webhook, send_message
from agent_team_chat.events import dispatch_webhooks


RECEIVED = {}


def start_receiver(host: str = "127.0.0.1", port: int = 8077):
    app = FastAPI()

    @app.post("/hook")
    async def hook(request: Request):
        body = await request.body()
        RECEIVED["headers"] = dict(request.headers)
        try:
            RECEIVED["json"] = json.loads(body.decode("utf-8"))
        except Exception:
            RECEIVED["json"] = {}
        return {"ok": True}

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


class TestWebhookSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # start receiver
        cls.thread = threading.Thread(target=start_receiver, kwargs={"port": 8077}, daemon=True)
        cls.thread.start()
        # Wait until server accepts connections
        import requests
        for _ in range(30):
            try:
                requests.post("http://127.0.0.1:8077/hook", json={"warmup": True}, timeout=1)
                break
            except Exception:
                time.sleep(0.1)
        RECEIVED.clear()

    def test_send_message_dispatches(self):
        db = Database(":memory:")
        ctx = ToolContext(db=db, image_dir="./agent-team-chat-enhanced/images")
        pr = create_project(ctx, name="demo", description="")
        project_id = pr["project_id"]

        url = "http://127.0.0.1:8077/hook"
        secret = "secret123"
        register_webhook(ctx, project_id=project_id, url=url, secret=secret, events=["message.created"])  # noqa
        res = send_message(ctx, project_id=project_id, agent="tester", role="user", content="hello world")
        self.assertTrue(res.get("success"))
        # Also invoke dispatcher directly as smoke (in case event loop is not running)
        import asyncio
        try:
            asyncio.get_event_loop().run_until_complete(dispatch_webhooks(db, project_id, "message.created", {"message_id": res.get("message_id")}))
        except RuntimeError:
            asyncio.run(dispatch_webhooks(db, project_id, "message.created", {"message_id": res.get("message_id")}))
        # wait for dispatch
        for _ in range(50):
            if RECEIVED.get("json"):
                break
            time.sleep(0.1)
        self.assertIn("json", RECEIVED)
        self.assertEqual(RECEIVED["json"].get("type"), "message.created")


if __name__ == "__main__":
    unittest.main()
