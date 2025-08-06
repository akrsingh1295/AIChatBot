"""
Security middleware for production deployment
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection for rate limiting
redis_client = None
if os.getenv("REDIS_URL"):
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL"))
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not redis_client:
            # If Redis is not available, skip rate limiting
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        if request.headers.get("X-Forwarded-For"):
            client_ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
        
        # Rate limiting key
        key = f"rate_limit:{client_ip}"
        
        try:
            # Get current count
            current = redis_client.get(key)
            
            if current is None:
                # First request
                redis_client.setex(key, 60, 1)
            else:
                count = int(current)
                if count >= self.calls_per_minute:
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Rate limit exceeded. Please try again later."}
                    )
                # Increment counter
                redis_client.incr(key)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # If Redis fails, allow the request
            pass
        
        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/Response logging middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url} - {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Size: {response.headers.get('content-length', 'unknown')}"
        )
        
        # Add response time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Validate API keys for sensitive endpoints"""
    
    def __init__(self, app, protected_paths: list = None):
        super().__init__(app)
        self.protected_paths = protected_paths or ["/initialize", "/chat", "/load-knowledge"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip validation for non-protected paths
        if not any(request.url.path.startswith(path) for path in self.protected_paths):
            return await call_next(request)
        
        # Check if this is an OPTIONS request (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # For now, we'll rely on the application-level API key validation
        # This middleware can be extended for additional API key checks
        
        return await call_next(request)

class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Health check endpoint that bypasses other middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/health":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "healthy",
                    "timestamp": time.time(),
                    "version": "1.0.0"
                }
            )
        
        return await call_next(request) 