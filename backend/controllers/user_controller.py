from models.models import User
from utils.responses import api_response

class UserController:
    @staticmethod
    def get_users():
        try:
            users = User.query.all()
            data = [{"id": u.id, "name": u.name, "email": u.email, "avatar_url": u.avatar_url} for u in users]
            return api_response(True, "Users fetched successfully", data)
        except Exception as e:
            return api_response(False, str(e), status_code=500)
