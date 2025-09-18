import time
from typing import Optional, Tuple

from .database import Database


class RateLimiter:
    def __init__(self, db: Database, capacity: int = 5, interval_seconds: int = 60, global_limit_per_min: int = 60):
        self.db = db
        self.capacity = max(1, capacity)
        self.interval_seconds = max(1, interval_seconds)
        self.global_limit_per_min = max(1, global_limit_per_min)
        self._global_counter = {}  # Simple in-memory counter for global rate limiting

    def _refill(self, tokens: float, last_refill_ts: Optional[int]) -> Tuple[float, int]:
        now = int(time.time())
        if last_refill_ts is None:
            return float(self.capacity), now
        elapsed = max(0, now - int(last_refill_ts))
        rate_per_sec = self.capacity / float(self.interval_seconds)
        new_tokens = min(self.capacity, tokens + elapsed * rate_per_sec)
        if int(new_tokens) == self.capacity:
            # align refill ts to now when full
            return float(self.capacity), now
        return new_tokens, now

    def _check_global_limit(self) -> Tuple[bool, Optional[float]]:
        """Check global rate limit as a circuit breaker."""
        now = int(time.time())
        minute_bucket = now // 60

        # Clean old buckets (keep only current and previous minute)
        old_buckets = [k for k in self._global_counter.keys() if k < minute_bucket - 1]
        for bucket in old_buckets:
            del self._global_counter[bucket]

        # Check current minute
        current_count = self._global_counter.get(minute_bucket, 0)
        if current_count >= self.global_limit_per_min:
            # Calculate retry time (seconds until next minute)
            retry_after = 60 - (now % 60)
            return False, float(retry_after)

        # Increment counter
        self._global_counter[minute_bucket] = current_count + 1
        return True, None

    def check_and_consume(self, agent: str, project_id: Optional[int], cost: int = 1) -> Tuple[bool, Optional[float]]:
        # Check global rate limit first (circuit breaker)
        global_ok, global_retry = self._check_global_limit()
        if not global_ok:
            return False, global_retry

        # Check per-agent-per-project rate limit
        state = self.db.get_agent_status(agent, project_id)
        if state and state.get("rate_tokens") is not None:
            tokens = float(state.get("rate_tokens"))
        else:
            tokens = 0.0
        last_refill_ts = state.get("rate_refill_ts") if state else None
        tokens, now_sec = self._refill(tokens, last_refill_ts)

        if tokens >= cost:
            tokens -= cost
            self.db.upsert_agent_status(
                agent=agent,
                project_id=project_id,
                status=state.get("status") if state else None,
                details=state.get("details") if state else None,
                last_seen=int(time.time() * 1000),
                rate_tokens=tokens,
                rate_refill_ts=now_sec,
            )
            return True, None

        needed = cost - tokens
        rate_per_sec = self.capacity / float(self.interval_seconds)
        retry_after = needed / rate_per_sec

        # persist unchanged tokens and updated refill timestamp
        self.db.upsert_agent_status(
            agent=agent,
            project_id=project_id,
            status=state.get("status") if state else None,
            details=state.get("details") if state else None,
            last_seen=int(time.time() * 1000),
            rate_tokens=tokens,
            rate_refill_ts=now_sec,
        )
        return False, max(0.001, float(retry_after))
