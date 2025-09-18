"""
ProServe E2E Security and Authentication Tests
Authentication, authorization, security middleware, and threat protection
"""

import pytest
import json
import requests
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_jwt_authentication_system(framework: ProServeTestFramework):
    """Test JWT-based authentication and authorization"""
    
    # JWT Authentication handler
    auth_handler = '''
import json
import jwt
import hashlib
from datetime import datetime, timedelta

# Secret key for JWT (in production, this should be from environment)
JWT_SECRET = "proserve-test-secret-key-2025"
ALGORITHM = "HS256"

# Mock user database
users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "permissions": ["read", "write", "delete", "admin"]
    },
    "user": {
        "id": 2,
        "username": "user",
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user", 
        "permissions": ["read", "write"]
    },
    "guest": {
        "id": 3,
        "username": "guest",
        "password_hash": hashlib.sha256("guest123".encode()).hexdigest(),
        "role": "guest",
        "permissions": ["read"]
    }
}

def create_jwt_token(user_data):
    """Create JWT token for user"""
    payload = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
        "permissions": user_data["permissions"],
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

def check_permission(user_permissions, required_permission):
    """Check if user has required permission"""
    return required_permission in user_permissions

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/auth/login" and method == "POST":
        try:
            data = await request.json()
        except:
            return {"error": "Invalid JSON"}, 400
        
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return {"error": "Username and password required"}, 400
        
        # Verify credentials
        user = users_db.get(username)
        if not user:
            return {"error": "Invalid credentials"}, 401
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user["password_hash"]:
            return {"error": "Invalid credentials"}, 401
        
        # Create JWT token
        token = create_jwt_token(user)
        
        return {
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "permissions": user["permissions"]
            },
            "expires_in": 86400  # 24 hours
        }
    
    elif path == "/api/auth/verify" and method == "POST":
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid authorization header"}, 401
        
        token = auth_header.split(" ")[1]
        payload = verify_jwt_token(token)
        
        if "error" in payload:
            return payload, 401
        
        return {
            "valid": True,
            "user": {
                "id": payload["user_id"],
                "username": payload["username"],
                "role": payload["role"],
                "permissions": payload["permissions"]
            }
        }
    
    elif path == "/api/protected/admin" and method == "GET":
        # Admin-only endpoint
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Authentication required"}, 401
        
        token = auth_header.split(" ")[1]
        payload = verify_jwt_token(token)
        
        if "error" in payload:
            return payload, 401
        
        if not check_permission(payload["permissions"], "admin"):
            return {"error": "Admin access required"}, 403
        
        return {
            "message": "Welcome to admin area",
            "user": payload["username"],
            "admin_data": {
                "total_users": len(users_db),
                "system_status": "healthy",
                "last_backup": "2025-01-17T10:00:00Z"
            }
        }
    
    elif path == "/api/protected/user" and method == "GET":
        # User endpoint (requires read permission)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Authentication required"}, 401
        
        token = auth_header.split(" ")[1]
        payload = verify_jwt_token(token)
        
        if "error" in payload:
            return payload, 401
        
        if not check_permission(payload["permissions"], "read"):
            return {"error": "Read access required"}, 403
        
        return {
            "message": "User data accessed successfully",
            "user": payload["username"],
            "role": payload["role"],
            "user_data": {
                "profile_complete": True,
                "last_login": "2025-01-17T12:00:00Z"
            }
        }
    
    elif path == "/api/protected/write" and method == "POST":
        # Write endpoint (requires write permission)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Authentication required"}, 401
        
        token = auth_header.split(" ")[1]
        payload = verify_jwt_token(token)
        
        if "error" in payload:
            return payload, 401
        
        if not check_permission(payload["permissions"], "write"):
            return {"error": "Write access required"}, 403
        
        try:
            data = await request.json()
        except:
            return {"error": "Invalid JSON"}, 400
        
        return {
            "message": "Data written successfully",
            "user": payload["username"],
            "data_written": data,
            "timestamp": str(datetime.utcnow())
        }
    
    return {"error": "Endpoint not found"}, 404
'''
    
    manifest_path = framework.create_test_manifest(
        'test-jwt-auth',
        endpoints=[
            {'path': '/api/auth/login', 'method': 'post', 'handler': 'jwt_handler.handle'},
            {'path': '/api/auth/verify', 'method': 'post', 'handler': 'jwt_handler.handle'},
            {'path': '/api/protected/admin', 'method': 'get', 'handler': 'jwt_handler.handle'},
            {'path': '/api/protected/user', 'method': 'get', 'handler': 'jwt_handler.handle'},
            {'path': '/api/protected/write', 'method': 'post', 'handler': 'jwt_handler.handle'},
        ]
    )
    
    framework.create_test_handler('jwt_handler.py', auth_handler)
    
    service = await framework.start_test_service(manifest_path, 'jwt_auth_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test login with valid credentials
    login_data = {"username": "admin", "password": "admin123"}
    login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    login_result = login_response.json()
    admin_token = login_result["token"]
    assert "token" in login_result
    assert login_result["user"]["role"] == "admin"
    assert "admin" in login_result["user"]["permissions"]
    
    # Test login with invalid credentials
    invalid_login = {"username": "admin", "password": "wrongpassword"}
    invalid_response = requests.post(f"{base_url}/api/auth/login", json=invalid_login)
    assert invalid_response.status_code == 401
    
    # Test token verification
    headers = {"Authorization": f"Bearer {admin_token}"}
    verify_response = requests.post(f"{base_url}/api/auth/verify", headers=headers)
    assert verify_response.status_code == 200
    assert verify_response.json()["valid"] == True
    
    # Test admin endpoint with admin token
    admin_response = requests.get(f"{base_url}/api/protected/admin", headers=headers)
    assert admin_response.status_code == 200
    assert "admin_data" in admin_response.json()
    
    # Test user endpoint with admin token (should work - admin has all permissions)
    user_response = requests.get(f"{base_url}/api/protected/user", headers=headers)
    assert user_response.status_code == 200
    
    # Login as regular user
    user_login = {"username": "user", "password": "user123"}
    user_login_response = requests.post(f"{base_url}/api/auth/login", json=user_login)
    user_token = user_login_response.json()["token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test user endpoint with user token
    user_access_response = requests.get(f"{base_url}/api/protected/user", headers=user_headers)
    assert user_access_response.status_code == 200
    
    # Test admin endpoint with user token (should fail)
    user_admin_response = requests.get(f"{base_url}/api/protected/admin", headers=user_headers)
    assert user_admin_response.status_code == 403
    
    # Test write endpoint
    write_data = {"message": "Test write operation"}
    write_response = requests.post(f"{base_url}/api/protected/write", json=write_data, headers=user_headers)
    assert write_response.status_code == 200
    
    # Login as guest (read-only)
    guest_login = {"username": "guest", "password": "guest123"}
    guest_login_response = requests.post(f"{base_url}/api/auth/login", json=guest_login)
    guest_token = guest_login_response.json()["token"]
    guest_headers = {"Authorization": f"Bearer {guest_token}"}
    
    # Test write endpoint with guest token (should fail)
    guest_write_response = requests.post(f"{base_url}/api/protected/write", json=write_data, headers=guest_headers)
    assert guest_write_response.status_code == 403
    
    # Test access without token
    no_auth_response = requests.get(f"{base_url}/api/protected/user")
    assert no_auth_response.status_code == 401
    
    return {
        "jwt_authentication_working": True,
        "admin_login_successful": login_response.status_code == 200,
        "invalid_credentials_rejected": invalid_response.status_code == 401,
        "token_verification_working": verify_response.json()["valid"] == True,
        "admin_access_control": admin_response.status_code == 200,
        "user_access_control": user_access_response.status_code == 200,
        "permission_enforcement": user_admin_response.status_code == 403,
        "write_permission_working": write_response.status_code == 200,
        "guest_write_blocked": guest_write_response.status_code == 403,
        "unauthorized_access_blocked": no_auth_response.status_code == 401
    }


@pytest.mark.asyncio
async def test_api_rate_limiting_and_security(framework: ProServeTestFramework):
    """Test API rate limiting and security measures"""
    
    security_handler = '''
import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

# Rate limiting storage
rate_limit_storage = defaultdict(deque)
blocked_ips = set()
security_events = []

# Configuration
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60   # seconds
BLOCK_THRESHOLD = 50     # requests before IP block
BLOCK_DURATION = 300     # seconds

def get_client_ip(request):
    """Get client IP address"""
    # In production, check X-Forwarded-For, X-Real-IP headers
    return request.remote or "127.0.0.1"

def check_rate_limit(client_ip):
    """Check if client is within rate limits"""
    now = time.time()
    
    # Clean old requests
    while (rate_limit_storage[client_ip] and 
           rate_limit_storage[client_ip][0] < now - RATE_LIMIT_WINDOW):
        rate_limit_storage[client_ip].popleft()
    
    # Check current rate
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False, len(rate_limit_storage[client_ip])
    
    # Add current request
    rate_limit_storage[client_ip].append(now)
    return True, len(rate_limit_storage[client_ip])

def check_ip_block(client_ip):
    """Check if IP is blocked"""
    return client_ip in blocked_ips

def block_ip(client_ip, reason):
    """Block IP address"""
    blocked_ips.add(client_ip)
    security_events.append({
        "type": "ip_block",
        "ip": client_ip,
        "reason": reason,
        "timestamp": str(datetime.now())
    })

def log_security_event(event_type, client_ip, details=None):
    """Log security event"""
    event = {
        "type": event_type,
        "ip": client_ip,
        "timestamp": str(datetime.now()),
        "details": details or {}
    }
    security_events.append(event)

async def handle(request):
    method = request.method
    path = str(request.url.path)
    client_ip = get_client_ip(request)
    
    # Check if IP is blocked
    if check_ip_block(client_ip):
        log_security_event("blocked_access_attempt", client_ip)
        return {"error": "IP blocked due to security policy"}, 403
    
    # Check rate limiting for API endpoints
    if path.startswith("/api/"):
        allowed, current_count = check_rate_limit(client_ip)
        
        if not allowed:
            log_security_event("rate_limit_exceeded", client_ip, {"count": current_count})
            
            # Block IP if too many rate limit violations
            if current_count > BLOCK_THRESHOLD:
                block_ip(client_ip, "Excessive rate limit violations")
            
            return {
                "error": "Rate limit exceeded",
                "limit": RATE_LIMIT_REQUESTS,
                "window": RATE_LIMIT_WINDOW,
                "retry_after": RATE_LIMIT_WINDOW
            }, 429
    
    if path == "/api/public" and method == "GET":
        # Public endpoint for testing rate limiting
        return {
            "message": "Public endpoint accessed successfully",
            "client_ip": client_ip,
            "timestamp": str(datetime.now()),
            "rate_limit_remaining": RATE_LIMIT_REQUESTS - check_rate_limit(client_ip)[1]
        }
    
    elif path == "/api/validate-input" and method == "POST":
        # Test input validation and XSS prevention
        try:
            data = await request.json()
        except:
            log_security_event("invalid_json", client_ip)
            return {"error": "Invalid JSON"}, 400
        
        # Check for potential XSS attempts
        dangerous_patterns = ["<script", "javascript:", "onclick=", "onerror="]
        
        for key, value in data.items():
            if isinstance(value, str):
                for pattern in dangerous_patterns:
                    if pattern.lower() in value.lower():
                        log_security_event("xss_attempt", client_ip, {"pattern": pattern, "value": value})
                        return {"error": "Potentially malicious input detected"}, 400
        
        # Check for SQL injection patterns
        sql_patterns = ["' OR '1'='1", "DROP TABLE", "UNION SELECT", "INSERT INTO"]
        
        for key, value in data.items():
            if isinstance(value, str):
                for pattern in sql_patterns:
                    if pattern.lower() in value.lower():
                        log_security_event("sql_injection_attempt", client_ip, {"pattern": pattern})
                        return {"error": "Potentially malicious SQL detected"}, 400
        
        return {
            "message": "Input validation passed",
            "validated_data": data,
            "security_check": "passed"
        }
    
    elif path == "/api/security/events" and method == "GET":
        # Security monitoring endpoint
        recent_events = security_events[-50:]  # Last 50 events
        
        event_summary = defaultdict(int)
        for event in recent_events:
            event_summary[event["type"]] += 1
        
        return {
            "recent_events": recent_events,
            "event_summary": dict(event_summary),
            "blocked_ips": list(blocked_ips),
            "total_events": len(security_events)
        }
    
    elif path == "/api/security/stats" and method == "GET":
        # Security statistics
        now = time.time()
        active_sessions = 0
        
        for ip, requests in rate_limit_storage.items():
            # Count IPs with recent activity
            if requests and requests[-1] > now - 300:  # 5 minutes
                active_sessions += 1
        
        return {
            "active_sessions": active_sessions,
            "blocked_ips_count": len(blocked_ips),
            "security_events_count": len(security_events),
            "rate_limit_config": {
                "requests_per_window": RATE_LIMIT_REQUESTS,
                "window_seconds": RATE_LIMIT_WINDOW,
                "block_threshold": BLOCK_THRESHOLD
            }
        }
    
    return {"error": "Endpoint not found"}, 404
'''
    
    manifest_path = framework.create_test_manifest(
        'test-security',
        endpoints=[
            {'path': '/api/public', 'method': 'get', 'handler': 'security_handler.handle'},
            {'path': '/api/validate-input', 'method': 'post', 'handler': 'security_handler.handle'},
            {'path': '/api/security/events', 'method': 'get', 'handler': 'security_handler.handle'},
            {'path': '/api/security/stats', 'method': 'get', 'handler': 'security_handler.handle'},
        ]
    )
    
    framework.create_test_handler('security_handler.py', security_handler)
    
    service = await framework.start_test_service(manifest_path, 'security_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test normal API access
    normal_response = await assert_http_response(f"{base_url}/api/public")
    assert "message" in normal_response
    
    # Test rate limiting by making many requests quickly
    rate_limit_responses = []
    for i in range(15):  # Exceed the rate limit (10 requests per window)
        response = requests.get(f"{base_url}/api/public")
        rate_limit_responses.append(response.status_code)
    
    # Should have some 429 responses (rate limited)
    rate_limited_count = rate_limit_responses.count(429)
    assert rate_limited_count > 0
    
    # Test input validation - safe input
    safe_input = {"name": "John Doe", "email": "john@example.com", "message": "Hello world"}
    safe_response = requests.post(f"{base_url}/api/validate-input", json=safe_input)
    assert safe_response.status_code == 200
    assert safe_response.json()["security_check"] == "passed"
    
    # Test XSS detection
    xss_input = {"comment": "<script>alert('XSS')</script>"}
    xss_response = requests.post(f"{base_url}/api/validate-input", json=xss_input)
    assert xss_response.status_code == 400
    assert "malicious input" in xss_response.json()["error"]
    
    # Test SQL injection detection
    sql_injection_input = {"query": "' OR '1'='1 --"}
    sql_response = requests.post(f"{base_url}/api/validate-input", json=sql_injection_input)
    assert sql_response.status_code == 400
    assert "malicious SQL" in sql_response.json()["error"]
    
    # Test security events monitoring
    events_response = await assert_http_response(f"{base_url}/api/security/events")
    assert len(events_response["recent_events"]) > 0
    assert "rate_limit_exceeded" in events_response["event_summary"] or rate_limited_count > 0
    
    # Test security statistics
    stats_response = await assert_http_response(f"{base_url}/api/security/stats")
    assert "active_sessions" in stats_response
    assert "rate_limit_config" in stats_response
    
    return {
        "security_system_working": True,
        "normal_access_allowed": normal_response.get("message") is not None,
        "rate_limiting_active": rate_limited_count > 0,
        "input_validation_working": safe_response.status_code == 200,
        "xss_protection_active": xss_response.status_code == 400,
        "sql_injection_protection": sql_response.status_code == 400,
        "security_monitoring_active": len(events_response["recent_events"]) > 0,
        "security_stats_available": "active_sessions" in stats_response,
        "threat_detection_working": (xss_response.status_code == 400 and 
                                   sql_response.status_code == 400)
    }
