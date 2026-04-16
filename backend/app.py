from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.models.models import db
from backend.utils.jwt_util import init_jwt
from backend.api.auth import auth
from backend.api.interview import iv
from backend.api.report import rp
from backend.api.admin import admin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # 开启跨域，前端直接对接
    init_jwt(app)
    db.init_app(app)

    # 注册接口蓝图
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(iv, url_prefix="/api/interview")
    app.register_blueprint(rp, url_prefix="/api/report")
    app.register_blueprint(admin, url_prefix="/api/admin")

    # 健康检测接口
    @app.route('/')
    def index():
        return '<h1>AI面试助手后端运行成功（已接入豆包智能体）</h1><p>接口前缀：/api</p>'

    # 自动创建数据库表
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
