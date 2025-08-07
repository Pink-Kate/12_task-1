from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
from collections import defaultdict
import time
from config import settings

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        window_start = now - window
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def get_remaining_requests(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests for the current window"""
        now = time.time()
        window_start = now - window
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        return max(0, limit - len(self.requests[key]))

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def check_rate_limit(request: Request, limit: int, window: int, key_prefix: str = ""):
    """Check rate limit for the request"""
    client_ip = get_client_ip(request)
    key = f"{key_prefix}:{client_ip}"
    
    if not rate_limiter.is_allowed(key, limit, window):
        remaining_time = window - (time.time() - rate_limiter.requests[key][0])
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {int(remaining_time)} seconds.",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + remaining_time))
            }
        )
    
    remaining = rate_limiter.get_remaining_requests(key, limit, window)
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_limit = limit 