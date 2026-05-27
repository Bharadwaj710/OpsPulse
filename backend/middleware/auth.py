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
            import requests

            # Verify token by fetching the user from Supabase REST API directly
            # This completely bypasses the broken supabase-py/gotrue python dependencies.
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": Config.SUPABASE_KEY
            }
            auth_url = f"{Config.SUPABASE_URL.rstrip('/')}/auth/v1/user"
            
            response = requests.get(auth_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Supabase Auth REST API failed: {response.status_code} - {response.text}")
                return jsonify({"success": False, "message": "Invalid token"}), 401
                
            user_data = response.json()
            request.user_id = user_data.get("id")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Auth error: {e}")
            return jsonify({"success": False, "message": "Authentication failed"}), 401

        return f(*args, **kwargs)
    return decorated