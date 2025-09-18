import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_team_chat.database import Database
from agent_team_chat.rate_limiter import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.rl = RateLimiter(self.db, capacity=5, interval_seconds=60)

    def test_token_bucket_limits(self):
        agent = "tester"
        project = 1
        # Consume 5 tokens
        for i in range(5):
            ok, retry = self.rl.check_and_consume(agent, project)
            self.assertTrue(ok)
            self.assertIsNone(retry)
        # 6th should fail
        ok, retry = self.rl.check_and_consume(agent, project)
        self.assertFalse(ok)
        self.assertIsNotNone(retry)
        self.assertGreater(retry, 0)

        # Fast-forward refill: simulate 60s
        # Update last_refill_ts to now - 60 so tokens refill to capacity
        st = self.db.get_agent_status(agent, project)
        self.db.upsert_agent_status(agent, project, None, None, None, st["rate_tokens"], int(time.time()) - 60)
        ok, retry = self.rl.check_and_consume(agent, project)
        self.assertTrue(ok)
        self.assertIsNone(retry)


if __name__ == "__main__":
    unittest.main()
