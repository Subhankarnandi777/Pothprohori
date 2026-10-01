"""
Rate limiting for Pothprohori API using slowapi (in-memory).
No Redis required for development – swap the storage backend for Redis in production.

Limits:
  /auth/*   → 10 requests / minute  (brute-force protection)
  /chat/*   → 20 requests / minute  (LLM cost protection)
  global    → 200 requests / minute (general abuse protection)
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --------------------------------------------------------------------------- #
# Limiter instance — import this wherever you need @limiter.limit(...)
# --------------------------------------------------------------------------- #
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    headers_enabled=True,          # adds X-RateLimit-* response headers
)

__all__ = ["limiter", "RateLimitExceeded", "_rate_limit_exceeded_handler"]
