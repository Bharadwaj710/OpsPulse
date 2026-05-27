import jwt
from flask import request, jsonify
from functools import wraps
from config.config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Expecting "Bearer <token>"
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"success": False, "message": "Authentication token is missing"}), 401

        try:
            from supabase import create_client, Client
            
            # Initialize Supabase client
            supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            
            # Verify token by fetching the user from Supabase directly
            user_response = supabase.auth.get_user(token)
            
            if not user_response.user:
                return jsonify({"success": False, "message": "Invalid token"}), 401
                
            request.user_id = user_response.user.id
            
        except Exception as e:
            print(f"Auth error: {e}")
            return jsonify({"success": False, "message": "Authentication failed"}), 401

        return f(*args, **kwargs)
    return decorated