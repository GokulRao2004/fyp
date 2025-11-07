"""
Clerk Authentication Middleware for Flask
Validates JWT tokens from Clerk
"""
import os
import logging
from functools import wraps
from flask import request, jsonify
import jwt
from jwt import PyJWKClient
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ClerkAuth:
    """Clerk authentication handler"""
    
    def __init__(self):
        self.clerk_domain = os.getenv('CLERK_DOMAIN')
        self.jwks_url = f"https://{self.clerk_domain}/.well-known/jwks.json" if self.clerk_domain else None
        self.jwks_client = PyJWKClient(self.jwks_url) if self.jwks_url else None
        
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify Clerk JWT token
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        if not self.jwks_client:
            logger.warning("Clerk not configured, skipping authentication")
            return {"user_id": "anonymous", "auth_disabled": True}
        
        try:
            # Get signing key
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_exp": True}
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None

# Global auth instance
clerk_auth = ClerkAuth()

def require_auth(f):
    """
    Decorator to require authentication on routes
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return jsonify({"user": request.user})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = clerk_auth.verify_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Attach user info to request
        request.user = payload
        request.user_id = payload.get('sub') or payload.get('user_id', 'anonymous')
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """
    Decorator for optional authentication
    Routes work without auth but attach user info if available
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = clerk_auth.verify_token(token)
            
            if payload:
                request.user = payload
                request.user_id = payload.get('sub') or payload.get('user_id', 'anonymous')
            else:
                request.user = None
                request.user_id = 'anonymous'
        else:
            request.user = None
            request.user_id = 'anonymous'
        
        return f(*args, **kwargs)
    
    return decorated_function
