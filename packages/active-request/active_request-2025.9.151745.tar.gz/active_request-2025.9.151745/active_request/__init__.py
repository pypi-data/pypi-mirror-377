from __future__ import annotations

import time
import uuid
from typing import Optional

import redis
from redis.asyncio import Redis as AsyncRedis

# Lua script: ZADD(now_ms, uuid), ZREMRANGEBYSCORE(old), ZCARD, EXPIRE, optional SETEX gauge
_LUA_SLIDING_WINDOW = """
local key = KEYS[1]
local gauge_key = KEYS[2]
local now_ms = tonumber(ARGV[1])
local member = ARGV[2]
local window_ms = tonumber(ARGV[2 + 1])

local cutoff = now_ms - window_ms
redis.call("ZADD", key, now_ms, member)
redis.call("ZREMRANGEBYSCORE", key, 0, cutoff)
local count = redis.call("ZCARD", key)
redis.call("EXPIRE", key, math.floor(window_ms / 1000) + 5)
if gauge_key ~= "" then
  redis.call("SETEX", gauge_key, math.floor(window_ms / 1000) + 5, tostring(count))
end
return count
"""


def record_active_request(
    r: redis.Redis,
    *,
    key: str = "metrics:active_requests",
    window_seconds: int = 60,
    gauge_key: Optional[str] = "metrics:active_requests:count",
) -> int:
    """
    Record one request and return the current number of requests in the last `window_seconds`.
    Safe across multiple processes.
    """
    now_ms = int(time.time() * 1000)
    member = f"{now_ms}:{uuid.uuid4()}"
    window_ms = window_seconds * 1000
    res = r.eval(
        _LUA_SLIDING_WINDOW,
        2,
        key,
        gauge_key or "",
        now_ms,
        member,
        window_ms,
    )
    return int(res)


async def arecord_active_request(
    r: AsyncRedis,
    *,
    key: str = "metrics:active_requests",
    window_seconds: int = 60,
    gauge_key: Optional[str] = "metrics:active_requests:count",
) -> int:
    """
    Async variant (e.g., FastAPI with redis.asyncio).
    """
    now_ms = int(time.time() * 1000)
    member = f"{now_ms}:{uuid.uuid4()}"
    window_ms = window_seconds * 1000
    res = await r.eval(
        _LUA_SLIDING_WINDOW,
        2,
        key,
        gauge_key or "",
        now_ms,
        member,
        window_ms,
    )
    return int(res)
