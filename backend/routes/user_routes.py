from flask import Blueprint
from controllers.user_controller import UserController
from middleware.auth import token_required

user_bp = Blueprint('users', __name__)

user_bp.route('', methods=['GET'], strict_slashes=False)(token_required(UserController.get_users))
