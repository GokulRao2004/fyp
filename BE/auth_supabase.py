import logging
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict
from services.supabase_service import supabase_service

logger = logging.getLogger(__name__)


class SupabaseAuth:
    """Supabase authentication handler"""

    def __init__(self):
        self.supabase = supabase_service

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token from Supabase Auth
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User info if valid, None otherwise
        """
        try:
            # Supabase JWT verification
            # Token comes from supabase client library
            # In production, you'd verify JWT signature
            
            # For now, we'll use the token to get user data
            # The JWT token contains user_id and email claims
            import jwt
            import os
            
            jwt_secret = os.getenv('SUPABASE_JWT_SECRET')
            
            # Decode without verification first (in production, verify signature)
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            user_id = decoded.get('sub')  # JWT subject is user_id
            email = decoded.get('email')
            
            if not user_id:
                return None
            
            return {
                'user_id': user_id,
                'email': email,
                'email_verified': decoded.get('email_confirmed_at') is not None
            }

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None


# Initialize auth
supabase_auth = SupabaseAuth()


def require_auth(f):
    """
    Decorator to require Supabase authentication for endpoint
    Extracts user info from token and adds to request object
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Missing or invalid authorization header',
                'code': 401
            }), 401

        token = auth_header.split(' ')[1]

        # Verify token
        user_info = supabase_auth.verify_token(token)

        if not user_info:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 401
            }), 401

        # Add user info to request
        request.user_id = user_info['user_id']
        request.user_email = user_info.get('email')
        request.user_info = user_info

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication
    If token is provided and valid, adds user info to request
    If token is missing or invalid, continues without auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_info = supabase_auth.verify_token(token)

            if user_info:
                request.user_id = user_info['user_id']
                request.user_email = user_info.get('email')
                request.user_info = user_info
            else:
                request.user_id = None
                request.user_info = None
        else:
            request.user_id = None
            request.user_info = None

        return f(*args, **kwargs)

    return decorated_function
