from flask import Blueprint
from controllers.auth_controller import AuthController
from middleware.auth import token_required

auth_bp = Blueprint('auth', __name__)

# This endpoint is called by the frontend after Google Login
auth_bp.route('/auth/sync', methods=['POST'])(token_required(AuthController.sync_user))