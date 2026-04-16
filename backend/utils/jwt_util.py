from flask_jwt_extended import JWTManager


def init_jwt(app):
    return JWTManager(app)
