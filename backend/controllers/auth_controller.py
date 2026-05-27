from flask import request
from models.models import db, User
from utils.responses import api_response

class AuthController:
    @staticmethod
    def sync_user():
        data = request.get_json(silent=True)
        user_id = getattr(request, 'user_id', None)
        print(f"DEBUG: sync_user called. user_id={user_id}, data={data}")
        
        if not data or 'email' not in data:
            return api_response(False, f"Email is required. Received: {data}", status_code=400)

        try:
            # Check if user already exists in our public.users table
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                # Create the user in our DB if they don't exist
                user = User(
                    id=user_id,
                    name=data.get('name', 'New User'),
                    email=data.get('email'),
                    avatar_url=data.get('avatar_url')
                )
                db.session.add(user)
                db.session.commit()
                return api_response(True, "User synced successfully", {"id": user.id})
            
            return api_response(True, "User already synced", {"id": user.id})
            
        except Exception as e:
            print(f"Sync Error: {str(e)}")
            return api_response(False, f"Internal server error: {str(e)}", status_code=500)