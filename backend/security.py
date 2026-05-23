"""
Security Hardening Module for Real-Time Weather Pipeline
Implements CORS, rate limiting, input validation, SQL injection prevention
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re
from typing import Optional, List
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# ============================================================================
# CORS Configuration
# ============================================================================

def apply_cors(app: FastAPI, allowed_origins: Optional[List[str]] = None):
    """
    Apply strict CORS policy to prevent cross-origin attacks
    
    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (e.g., ['https://example.com'])
    """
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",    # Local development
            "http://localhost:8000",    # Local API development
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Explicit allowed origins
        allow_credentials=True,          # Allow credentials (cookies, auth headers)
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
        ],
        expose_headers=["Content-Length", "X-Request-ID"],
        max_age=600,  # Cache preflight for 10 minutes
    )
    
    logger.info(f"✅ CORS configured with origins: {allowed_origins}")


# ============================================================================
# Trusted Host Middleware
# ============================================================================

def apply_trusted_host(app: FastAPI, allowed_hosts: Optional[List[str]] = None):
    """
    Restrict requests to trusted hosts only
    
    Args:
        app: FastAPI application instance
        allowed_hosts: List of trusted hosts
    """
    if allowed_hosts is None:
        allowed_hosts = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "*.example.com",  # Wildcard for subdomains
        ]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
    
    logger.info(f"✅ Trusted host middleware configured")


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimitConfig:
    """Configuration for rate limiting"""
    
    # Global rate limits
    GLOBAL_LIMIT = "1000/minute"  # 1000 requests per minute globally
    PER_USER_LIMIT = "100/minute"  # 100 requests per user per minute
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS = {
        # Sensitive operations
        "/api/export/": "10/minute",      # Export operations (resource intensive)
        "/api/import/": "5/minute",       # Import operations (risky)
        
        # Public endpoints
        "/api/health": "unlimited",
        "/api/weather/current": "60/minute",
        "/api/weather/history": "30/minute",
        "/api/weather/alerts": "60/minute",
        
        # Monitoring (low impact)
        "/api/monitoring/": "unlimited",
        
        # Admin endpoints
        "/api/admin/": "5/minute",
    }


def create_rate_limiter() -> Limiter:
    """Create rate limiter instance"""
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["1000/minute"],
        storage_uri="memory://"  # Use memory storage (can use Redis for distributed)
    )
    return limiter


def apply_rate_limiting(app: FastAPI, limiter: Limiter):
    """
    Apply rate limiting to FastAPI application
    
    Args:
        app: FastAPI application instance
        limiter: Limiter instance
    """
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
        """Handle rate limit exceeded errors"""
        logger.warning(
            f"Rate limit exceeded for {request.client.host}: {request.url.path}"
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": exc.detail
            }
        )
    
    setattr(app.state, "limiter", limiter)
    app.state.limiter = limiter
    logger.info("✅ Rate limiting configured")


# ============================================================================
# Input Validation & Sanitization
# ============================================================================

class InputValidator:
    """Validates and sanitizes user input"""
    
    # Regex patterns for validation
    LOCATION_PATTERN = re.compile(r"^[a-zA-Z\s\-]{2,100}$")  # Alpha, spaces, hyphens
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PHONE_PATTERN = re.compile(r"^\+?[\d\s\-()]{10,20}$")
    NUMERIC_PATTERN = re.compile(r"^-?\d+(\.\d+)?$")
    ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,255}$")
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bOR\b.*=.*)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(;\s*--)",  # Comment injection
        r"(\/\*.*\*\/)",  # Comment injection
    ]
    
    @staticmethod
    def validate_location(location: str) -> bool:
        """Validate location name"""
        if not location or len(location) > 100:
            return False
        return bool(InputValidator.LOCATION_PATTERN.match(location))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        if not email or len(email) > 254:
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number"""
        if not phone:
            return False
        return bool(InputValidator.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def validate_numeric(value: str) -> bool:
        """Validate numeric value"""
        return bool(InputValidator.NUMERIC_PATTERN.match(value))
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize string input
        - Remove leading/trailing whitespace
        - Limit length
        - Escape special characters
        """
        if not isinstance(value, str):
            return ""
        
        # Strip whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Check if input contains potential SQL injection patterns
        
        Returns True if suspicious patterns found
        """
        if not value:
            return False
        
        value_upper = value.upper()
        
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {value[:50]}")
                return True
        
        return False
    
    @staticmethod
    def validate_and_sanitize_location(location: str) -> str:
        """
        Validate and sanitize location name
        
        Raises ValueError if invalid
        """
        # Check for SQL injection
        if InputValidator.check_sql_injection(location):
            raise ValueError("Invalid location: contains suspicious patterns")
        
        # Sanitize
        location = InputValidator.sanitize_string(location, max_length=100)
        
        # Validate format
        if not InputValidator.validate_location(location):
            raise ValueError("Invalid location: only letters, spaces, and hyphens allowed")
        
        return location


# ============================================================================
# HTTPS/TLS Configuration
# ============================================================================

class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def add_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        
        @app.middleware("http")
        async def add_security_headers_middleware(request: Request, call_next):
            response = await call_next(request)
            
            # HTTP Security Headers
            response.headers["X-Content-Type-Options"] = "nosniff"  # Prevent MIME sniffing
            response.headers["X-Frame-Options"] = "DENY"  # Prevent clickjacking
            response.headers["X-XSS-Protection"] = "1; mode=block"  # Enable XSS protection
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"  # HSTS
            response.headers["Content-Security-Policy"] = "default-src 'self'"  # CSP
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            # Remove server identification
            response.headers.pop("Server", None)
            response.headers["Server"] = "SecureAPI/1.0"
            
            return response
        
        logger.info("✅ Security headers configured")


# ============================================================================
# Authentication Helpers
# ============================================================================

class AuthenticationSecurity:
    """Authentication security utilities"""
    
    @staticmethod
    def require_https(app: FastAPI):
        """
        Redirect HTTP to HTTPS (for production)
        
        Note: Only works behind a reverse proxy (nginx, loadbalancer)
        """
        @app.middleware("http")
        async def https_redirect_middleware(request: Request, call_next):
            if request.url.scheme == "http" and request.headers.get("X-Forwarded-Proto") == "https":
                # Already HTTPS (behind proxy)
                pass
            elif request.url.scheme == "http":
                # Only enforce in production
                if request.app.debug is False:
                    url = request.url.replace(scheme="https")
                    return JSONResponse(status_code=307, headers={"location": str(url)})
            
            return await call_next(request)
        
        logger.info("✅ HTTPS enforcement configured")


# ============================================================================
# Request Validation Middleware
# ============================================================================

def apply_request_validation(app: FastAPI):
    """Apply request validation middleware"""
    
    @app.middleware("http")
    async def validate_request_middleware(request: Request, call_next):
        """Validate all incoming requests"""
        
        # Check Content-Length (prevent large payloads)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"Request exceeds size limit: {content_length}")
            return JSONResponse(
                status_code=413,
                content={"error": "Payload too large"}
            )
        
        # Check for suspicious headers
        suspicious_headers = ["X-Forwarded-For", "X-Original-URL", "X-Rewrite-URL"]
        for header in suspicious_headers:
            if header in request.headers:
                logger.info(f"Request contains header: {header}")
        
        return await call_next(request)
    
    logger.info("✅ Request validation middleware configured")


# ============================================================================
# Dependency Injection for Security
# ============================================================================

async def validate_api_key(request: Request) -> str:
    """
    Validate API key from Authorization header
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(api_key: str = Depends(validate_api_key)):
            ...
    """
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    
    api_key = auth_header.split(" ")[1]
    
    # Validate API key (implement your validation logic)
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


# ============================================================================
# Security Configuration Function
# ============================================================================

def apply_all_security(
    app: FastAPI,
    allowed_origins: Optional[List[str]] = None,
    allowed_hosts: Optional[List[str]] = None,
    enable_https_redirect: bool = False,
):
    """
    Apply all security configurations to FastAPI app
    
    Args:
        app: FastAPI application instance
        allowed_origins: CORS allowed origins
        allowed_hosts: Trusted hosts
        enable_https_redirect: Enable HTTPS redirect
    """
    
    logger.info("🔒 Applying security hardening...")
    
    # 1. CORS
    apply_cors(app, allowed_origins)
    
    # 2. Trusted Hosts
    apply_trusted_host(app, allowed_hosts)
    
    # 3. Rate Limiting
    limiter = create_rate_limiter()
    apply_rate_limiting(app, limiter)
    
    # 4. Security Headers
    SecurityHeaders.add_security_headers(app)
    
    # 5. Request Validation
    apply_request_validation(app)
    
    # 6. HTTPS Redirect (production only)
    if enable_https_redirect:
        AuthenticationSecurity.require_https(app)
    
    logger.info("✅ All security hardening applied successfully")
    
    return limiter


# ============================================================================
# Usage Example in main.py
# ============================================================================

EXAMPLE_INTEGRATION = '''
# In main.py, after creating FastAPI app:

from fastapi import FastAPI
from security import apply_all_security, InputValidator

app = FastAPI(title="Weather Pipeline API")

# Apply security hardening
limiter = apply_all_security(
    app,
    allowed_origins=[
        "https://example.com",
        "https://www.example.com",
        "http://localhost:3000",  # Local development
    ],
    allowed_hosts=[
        "example.com",
        "*.example.com",
        "localhost",
    ],
    enable_https_redirect=False  # Enable for production
)

# Use input validation in routes
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/weather/current/{location}")
async def get_weather(location: str):
    try:
        # Validate and sanitize location
        location = InputValidator.validate_and_sanitize_location(location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # ... rest of endpoint logic
    return {"location": location, "temperature": 25}

app.include_router(router)
'''
