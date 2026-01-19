from fastapi import FastAPI, HTTPException, Depends, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime, date, timedelta
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from collections import defaultdict
import time
import secrets
import hashlib
import re
from passlib.context import CryptContext
import jwt
from jwt import PyJWKClient
import requests
from dotenv import load_dotenv
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables
load_dotenv()

# ========================================
# LOGGING CONFIGURATION
# ========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CashFlow Manager API", 
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)

# Get allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
TRUSTED_HOSTS = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")

# ========================================
# SECURITY MIDDLEWARE
# ========================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://jvlbxzhqzfaxvneqcyiy.supabase.co"
        )
        
        # HSTS (HTTP Strict Transport Security) - only in production
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security monitoring"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
        
        response = await call_next(request)
        
        # Log response time and status
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.2f}s"
        )
        
        return response

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host middleware (prevents host header injection)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# SECURITY CONFIGURATION
# ========================================

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Supabase JWT Configuration
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# Database Configuration
DATABASE_URL = os.getenv("SUPABASE_DB_URL", "")

# Validate required environment variables
if not all([SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_JWT_SECRET, DATABASE_URL]):
    print("WARNING: Missing required environment variables. Please check your .env file.")

# Security Constants
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
MAX_STRING_LENGTH = 1000
ALLOWED_FILE_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json'}

# ========================================
# INPUT VALIDATION & SANITIZATION
# ========================================

def sanitize_string(input_str: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """Sanitize string input to prevent XSS and injection attacks"""
    if not input_str:
        return ""
    
    # Remove null bytes
    sanitized = input_str.replace('\x00', '')
    
    # Trim to max length
    sanitized = sanitized[:max_length]
    
    # Remove potentially dangerous characters for SQL/XSS (basic sanitization)
    # Note: We use parameterized queries, but this adds extra protection
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Remove script tags
        r'javascript:',                 # Remove javascript: protocol
        r'on\w+\s*=',                  # Remove event handlers
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements"""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must be less than {MAX_PASSWORD_LENGTH} characters"
    
    # Check for complexity
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must contain uppercase, lowercase, digit, and special character"
    
    return True, "Password is strong"

def validate_amount(amount: float) -> bool:
    """Validate transaction amount"""
    return 0 < amount <= 1_000_000_000  # Max 1 billion

def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> bool:
    """Validate date range is logical"""
    if start_date and end_date:
        return start_date <= end_date
    return True

# ========================================
# DATABASE CONNECTION POOL
# ========================================

# Connection pool for better performance
db_pool = None

def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )
        print("✓ Database connection pool initialized")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database pool: {e}")
        return False

@contextmanager
def get_db_connection():
    """Get a database connection from the pool"""
    connection = None
    try:
        connection = db_pool.getconn()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            db_pool.putconn(connection)

# Cache for JWKS
_jwks_cache = None
_jwks_cache_time = None

def get_jwks():
    """Fetch JWKS from Supabase"""
    global _jwks_cache, _jwks_cache_time
    
    # Cache for 1 hour
    if _jwks_cache and _jwks_cache_time and (time.time() - _jwks_cache_time) < 3600:
        return _jwks_cache
    
    try:
        print(f"Fetching JWKS from: {SUPABASE_JWKS_URL}")
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
        }
        response = requests.get(SUPABASE_JWKS_URL, headers=headers, timeout=5)
        print(f"JWKS response status: {response.status_code}")
        print(f"JWKS response content: {response.text[:200]}")
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = time.time()
        print(f"Successfully cached JWKS with {len(_jwks_cache.get('keys', []))} keys")
        return _jwks_cache
    except Exception as e:
        print(f"Failed to fetch JWKS: {type(e).__name__}: {e}")
        return None

# HTTP Bearer for token authentication
security = HTTPBearer()

# ========================================
# AUDIT LOGGING
# ========================================

class AuditLogger:
    """Log security-relevant events for monitoring and compliance"""
    
    @staticmethod
    def log_event(event_type: str, user_id: Optional[str], details: dict, ip_address: str):
        """Log security event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details
        }
        logger.info(f"AUDIT: {log_entry}")
    
    @staticmethod
    def log_auth_success(user_id: str, ip_address: str):
        AuditLogger.log_event("AUTH_SUCCESS", user_id, {"action": "login"}, ip_address)
    
    @staticmethod
    def log_auth_failure(email: str, ip_address: str, reason: str):
        AuditLogger.log_event("AUTH_FAILURE", None, {"email": email, "reason": reason}, ip_address)
    
    @staticmethod
    def log_password_change(user_id: str, ip_address: str):
        AuditLogger.log_event("PASSWORD_CHANGE", user_id, {"action": "password_changed"}, ip_address)
    
    @staticmethod
    def log_data_access(user_id: str, resource: str, ip_address: str):
        AuditLogger.log_event("DATA_ACCESS", user_id, {"resource": resource}, ip_address)
    
    @staticmethod
    def log_data_modification(user_id: str, action: str, resource_id: str, ip_address: str):
        AuditLogger.log_event(
            "DATA_MODIFICATION", 
            user_id, 
            {"action": action, "resource_id": resource_id}, 
            ip_address
        )
    
    @staticmethod
    def log_suspicious_activity(user_id: Optional[str], activity: str, ip_address: str):
        AuditLogger.log_event("SUSPICIOUS_ACTIVITY", user_id, {"activity": activity}, ip_address)

# ========================================
# RATE LIMITING
# ========================================

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.failed_attempts = defaultdict(list)  # Track failed login attempts
        self.limits = {
            'default': {'requests': 100, 'window': 60},
            'transactions': {'requests': 100, 'window': 60},
            'summary': {'requests': 50, 'window': 60},
            'auth_login': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
            'auth_register': {'requests': 3, 'window': 3600},  # 3 per hour
        }
    
    def _clean_old_requests(self, ip: str, window: int):
        current_time = time.time()
        self.requests[ip] = [
            (timestamp, endpoint) 
            for timestamp, endpoint in self.requests[ip]
            if current_time - timestamp < window
        ]
    
    def check_failed_attempts(self, ip: str, max_attempts: int = 10, window: int = 3600) -> bool:
        """Check if IP has too many failed login attempts"""
        current_time = time.time()
        self.failed_attempts[ip] = [
            timestamp for timestamp in self.failed_attempts[ip]
            if current_time - timestamp < window
        ]
        return len(self.failed_attempts[ip]) < max_attempts
    
    def record_failed_attempt(self, ip: str):
        """Record a failed login attempt"""
        self.failed_attempts[ip].append(time.time())
    
    def check_rate_limit(self, ip: str, endpoint: str = 'default'):
        limit_key = 'default'
        if 'login' in endpoint:
            limit_key = 'auth_login'
        elif 'register' in endpoint:
            limit_key = 'auth_register'
        elif 'transactions' in endpoint:
            limit_key = 'transactions'
        elif 'summary' in endpoint:
            limit_key = 'summary'
        
        config = self.limits[limit_key]
        window = config['window']
        max_requests = config['requests']
        
        self._clean_old_requests(ip, window)
        
        current_time = time.time()
        recent_requests = len([
            t for t, e in self.requests[ip]
            if current_time - t < window
        ])
        
        if recent_requests >= max_requests:
            return False, max_requests, window
        
        self.requests[ip].append((current_time, endpoint))
        return True, max_requests - recent_requests - 1, window

rate_limiter = RateLimiter()

def check_rate_limit(request: Request):
    client_ip = request.client.host
    endpoint = request.url.path
    
    allowed, remaining, window = rate_limiter.check_rate_limit(client_ip, endpoint)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Please try again in {window} seconds.",
                "retry_after": window
            }
        )
    
    return True

# ========================================
# DATABASE SETUP & INITIALIZATION
# ========================================

def init_database_schema():
    """Initialize database schema for transactions"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Create transactions table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        user_id UUID NOT NULL,
                        type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                        amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
                        category VARCHAR(100) NOT NULL,
                        description TEXT,
                        date DATE NOT NULL,
                        payment_method VARCHAR(50),
                        currency VARCHAR(3) DEFAULT 'USD',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                # Create indexes for better query performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
                    ON transactions(user_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
                    ON transactions(user_id, date DESC);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_type 
                    ON transactions(type);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_category 
                    ON transactions(category);
                """)
                
                # Create updated_at trigger
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                """)
                
                cursor.execute("""
                    DROP TRIGGER IF EXISTS update_transactions_updated_at ON transactions;
                """)
                
                cursor.execute("""
                    CREATE TRIGGER update_transactions_updated_at
                    BEFORE UPDATE ON transactions
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                """)
                
                conn.commit()
                print("✓ Database schema initialized successfully")
                return True
    except Exception as e:
        print(f"✗ Failed to initialize database schema: {e}")
        return False

# ========================================
# AUTHENTICATION UTILITIES
# ========================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def hash_token(token: str) -> str:
    """Hash token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s AND is_active = 1", (user_id,))
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return dict(user)

async def verify_supabase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Supabase JWT token using JWKS and return user data"""
    token = credentials.credentials
    try:
        # Get the token header to find the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        alg = unverified_header.get('alg')
        
        # Fetch JWKS
        jwks = get_jwks()
        if not jwks:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to fetch JWKS"
            )
        
        # Find the right key
        signing_key = None
        key_data = None
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                key_data = key
                break
        
        if not key_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signing key not found in JWKS"
            )
        
        # Convert key based on type
        kty = key_data.get('kty')
        if kty == 'RSA':
            signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        elif kty == 'EC':
            signing_key = jwt.algorithms.ECAlgorithm.from_jwk(key_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported key type: {kty}"
            )
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[alg],  # Use the algorithm from the token header
            options={"verify_aud": False}
        )
        
        # Supabase stores user_id in 'sub' field
        return {"user_id": payload["sub"], "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except Exception as e:
        print(f"Token verification error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

# ========================================
# PYDANTIC MODELS
# ========================================

# Auth models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    full_name: str = Field(..., min_length=1, max_length=100)
    business_name: Optional[str] = Field(None, max_length=100)
    
    @validator('full_name', 'business_name')
    def sanitize_text_fields(cls, v):
        if v:
            return sanitize_string(v, 100)
        return v
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    business_name: Optional[str]
    is_verified: bool
    created_at: datetime

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    
    @validator('new_password')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

# Transaction models
class TransactionBase(BaseModel):
    type: str = Field(..., pattern="^(income|expense)$")
    amount: float = Field(..., gt=0, le=1_000_000_000)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field("", max_length=500)
    date: date
    payment_method: Optional[str] = Field("cash", max_length=50)
    currency: Optional[str] = Field("USD", min_length=3, max_length=3)
    
    @validator('category', 'description', 'payment_method')
    def sanitize_text_fields(cls, v):
        if v:
            return sanitize_string(v)
        return v
    
    @validator('amount')
    def validate_transaction_amount(cls, v):
        if not validate_amount(v):
            raise ValueError("Amount must be between 0 and 1 billion")
        return v
    
    @validator('currency')
    def validate_currency_code(cls, v):
        if v:
            v = v.upper()
            # Basic currency code validation (ISO 4217)
            if not re.match(r'^[A-Z]{3}$', v):
                raise ValueError("Currency must be a valid 3-letter code")
        return v

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = None

class Summary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int

# ========================================
# AUTH ENDPOINTS
# ========================================

@app.post("/auth/register", response_model=TokenResponse, dependencies=[Depends(check_rate_limit)])
async def register_user(user_data: UserRegister, request: Request):
    """Register a new user"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if email exists
            cursor.execute("SELECT email FROM users WHERE email = %s", (user_data.email,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create user
            user_id = secrets.token_urlsafe(16)
            password_hash = hash_password(user_data.password)
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (user_id, email, password_hash, full_name, business_name, 
                                 is_active, is_verified, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, 1, 1, %s, %s)
        """, (user_id, user_data.email, password_hash, user_data.full_name, 
              user_data.business_name, now, now))
        
        # Create tokens
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        # Store session
        session_id = secrets.token_urlsafe(32)
        expires_at = (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        
        cursor.execute("""
            INSERT INTO auth_sessions (session_id, user_id, access_token_hash, 
                                     refresh_token_hash, expires_at, created_at, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, hash_token(access_token), hash_token(refresh_token),
              expires_at, now, request.client.host))
        
        conn.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "user_id": user_id,
                "email": user_data.email,
                "full_name": user_data.full_name
            }
        }

@app.post("/auth/login", response_model=TokenResponse, dependencies=[Depends(check_rate_limit)])
async def login_user(credentials: UserLogin, request: Request):
    """Authenticate user and return tokens"""
    client_ip = request.client.host
    
    # Check for too many failed attempts
    if not rate_limiter.check_failed_attempts(client_ip):
        AuditLogger.log_suspicious_activity(None, "Too many failed login attempts", client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get user
            cursor.execute("SELECT * FROM users WHERE email = %s", (credentials.email,))
            user = cursor.fetchone()
        
        if not user or not verify_password(credentials.password, user["password_hash"]):
            rate_limiter.record_failed_attempt(client_ip)
            AuditLogger.log_auth_failure(credentials.email, client_ip, "Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user["is_active"]:
            AuditLogger.log_auth_failure(credentials.email, client_ip, "Account disabled")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been disabled"
            )
        
        # Log successful authentication
        AuditLogger.log_auth_success(user["user_id"], client_ip)
        
        # Update last login
        cursor.execute("UPDATE users SET last_login_at = %s WHERE user_id = %s",
                      (datetime.now().isoformat(), user["user_id"]))
        
        # Create tokens
        access_token = create_access_token(user["user_id"])
        refresh_token = create_refresh_token(user["user_id"])
        
        # Store session
        session_id = secrets.token_urlsafe(32)
        expires_at = (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO auth_sessions (session_id, user_id, access_token_hash, 
                                     refresh_token_hash, expires_at, created_at, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session_id, user["user_id"], hash_token(access_token), hash_token(refresh_token),
              expires_at, now, request.client.host))
        
        conn.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user["full_name"]
            }
        }

@app.post("/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user and invalidate session"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM auth_sessions WHERE user_id = %s", 
                          (current_user["user_id"],))
            conn.commit()
    
    return {"message": "Successfully logged out"}

@app.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "business_name": current_user["business_name"],
        "is_verified": bool(current_user["is_verified"]),
        "created_at": current_user["created_at"]
    }

@app.put("/auth/me")
async def update_user_profile(
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    allowed_fields = ["full_name", "business_name"]
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
            values = list(update_data.values()) + [datetime.now().isoformat(), current_user["user_id"]]
            
            cursor.execute(f"""
                UPDATE users 
                SET {set_clause}, updated_at = %s
                WHERE user_id = %s
            """, values)
            
            conn.commit()
    
    return {"message": "Profile updated successfully"}

@app.post("/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify current password
            if not verify_password(password_data.current_password, current_user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
        
        # Update password
        new_hash = hash_password(password_data.new_password)
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s, updated_at = %s
            WHERE user_id = %s
        """, (new_hash, datetime.now().isoformat(), current_user["user_id"]))
        
        # Invalidate all sessions
        cursor.execute("DELETE FROM auth_sessions WHERE user_id = %s", 
                      (current_user["user_id"],))
        
        conn.commit()
    
    return {"message": "Password changed successfully. Please login again."}

# ========================================
# TRANSACTION ENDPOINTS (Protected)
# ========================================

@app.post("/transactions", response_model=Transaction, dependencies=[Depends(check_rate_limit)])
async def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(verify_supabase_token)
):
    """Create a new transaction"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO transactions (user_id, type, amount, category, description, 
                                            date, payment_method, currency)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    current_user["user_id"],
                    transaction.type,
                    transaction.amount,
                    transaction.category,
                    transaction.description,
                    transaction.date,
                    transaction.payment_method,
                    transaction.currency
                ))
                row = cursor.fetchone()
                conn.commit()
                return dict(row)
    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions", response_model=List[Transaction], dependencies=[Depends(check_rate_limit)])
async def get_transactions(
    current_user: dict = Depends(verify_supabase_token),
    type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
):
    """Get user's transactions with filters"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM transactions WHERE user_id = %s"
                params = [current_user["user_id"]]
                
                if type:
                    query += " AND type = %s"
                    params.append(type)
                
                if category:
                    query += " AND category = %s"
                    params.append(category)
                
                if start_date:
                    query += " AND date >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND date <= %s"
                    params.append(end_date)
                
                query += " ORDER BY date DESC, created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/transactions/{transaction_id}", dependencies=[Depends(check_rate_limit)])
async def delete_transaction(
    transaction_id: int,
    current_user: dict = Depends(verify_supabase_token)
):
    """Delete a transaction"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM transactions WHERE id = %s AND user_id = %s",
                    (transaction_id, current_user["user_id"])
                )
                
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                
                conn.commit()
                return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary", response_model=Summary, dependencies=[Depends(check_rate_limit)])
async def get_summary(
    current_user: dict = Depends(verify_supabase_token),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get financial summary"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT type, SUM(amount) as total FROM transactions WHERE user_id = %s"
                params = [current_user["user_id"]]
                
                if start_date:
                    query += " AND date >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND date <= %s"
                    params.append(end_date)
                
                query += " GROUP BY type"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                income = 0
                expenses = 0
                
                for row in results:
                    if row["type"] == "income":
                        income = row["total"]
                    elif row["type"] == "expense":
                        expenses = row["total"]
                
                count_query = "SELECT COUNT(*) as count FROM transactions WHERE user_id = %s"
                count_params = [current_user["user_id"]]
                
                if start_date:
                    count_query += " AND date >= %s"
                    count_params.append(start_date)
                
                if end_date:
                    count_query += " AND date <= %s"
                    count_params.append(end_date)
                
                cursor.execute(count_query, count_params)
                count = cursor.fetchone()["count"]
                
                return {
                    "total_income": income,
                    "total_expenses": expenses,
                    "net_balance": income - expenses,
                    "transaction_count": count
                }
    except Exception as e:
        print(f"Error fetching summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories", dependencies=[Depends(check_rate_limit)])
async def get_categories(current_user: dict = Depends(verify_supabase_token)):
    """Get all unique categories for user"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT DISTINCT category, type FROM transactions WHERE user_id = %s ORDER BY category",
                    (current_user["user_id"],)
                )
                rows = cursor.fetchall()
                
                income_categories = []
                expense_categories = []
                
                for row in rows:
                    if row["type"] == "income":
                        income_categories.append(row["category"])
                    else:
                        expense_categories.append(row["category"])
                
                return {
                    "income": income_categories,
                    "expense": expense_categories
                }
    except Exception as e:
        print(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {
        "message": "CashFlow Manager API",
        "version": "1.0.0",
        "authentication": "enabled",
        "endpoints": {
            "auth": "/auth",
            "transactions": "/transactions",
            "summary": "/summary"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db_pool else "disconnected"
    }

# ========================================
# STARTUP & SHUTDOWN EVENTS
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    print("\n" + "="*50)
    print("🚀 Starting CashFlow Manager API")
    print("="*50)
    
    # Initialize database pool
    if init_db_pool():
        # Initialize schema
        init_database_schema()
    else:
        print("⚠️  WARNING: Failed to initialize database pool")
    
    print("="*50 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    global db_pool
    if db_pool:
        db_pool.closeall()
        print("✓ Database connections closed")

@app.get("/debug/token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Debug endpoint to check token payload"""
    token = credentials.credentials
    try:
        # Decode without verification to see payload
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Try to verify
        try:
            verified_payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            return {
                "status": "verified",
                "payload": verified_payload,
                "unverified_payload": unverified_payload
            }
        except Exception as e:
            return {
                "status": "verification_failed",
                "error": str(e),
                "unverified_payload": unverified_payload
            }
    except Exception as e:
        return {
            "status": "decode_failed",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)