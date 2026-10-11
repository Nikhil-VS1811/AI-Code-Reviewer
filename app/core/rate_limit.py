from collections import deque
import math
import threading
import time
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.services.auth_service import get_current_user


class RateLimiter:
    """Thread-safe in-memory per-user sliding-window rate limiter for expensive endpoints."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._requests: dict[str, deque[float]] = {}

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            history = self._requests.get(key)
            if history is None:
                history = deque()
                self._requests[key] = history

            while history and history[0] <= cutoff:
                history.popleft()

            if len(history) >= self.max_requests:
                retry_after = max(1, math.ceil(self.window_seconds - (now - history[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please wait before running another analysis.",
                    headers={"Retry-After": str(retry_after)},
                )

            history.append(now)

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> None:
        user_key = f"user:{current_user.id if current_user.id is not None else current_user.email}"
        self.check(user_key)


repository_scan_rate_limiter = RateLimiter(max_requests=5, window_seconds=60.0)
review_generation_rate_limiter = RateLimiter(max_requests=10, window_seconds=60.0)
