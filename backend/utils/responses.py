from flask import jsonify

def api_response(success, message, data=None, status_code=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data
    }), status_code