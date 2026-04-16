from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.models import db, User, InterviewSession, Report
from utils.resp import success, error

auth = Blueprint("auth", __name__)


# 注册
@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return error("参数缺失：用户名/密码不能为空")
    if len(username) < 2 or len(username) > 50:
        return error("用户名长度应为2-50个字符")
    if len(password) < 6:
        return error("密码长度不能少于6位")
    if User.query.filter_by(username=username).first():
        return error("用户已存在")
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return success(msg="注册成功")


# 登录
@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not check_password_hash(user.password, data.get("password")):
        return error("账号或密码错误")
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    return success({
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    })


# 获取当前用户信息
@auth.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return error("用户不存在")

    # 统计面试数据
    interview_count = InterviewSession.query.filter_by(user_id=uid).count()
    report_count = Report.query.filter_by(user_id=uid).count()
    avg_score = db.session.query(db.func.avg(Report.score)).filter_by(user_id=uid).scalar()

    return success({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "interview_count": interview_count,
            "report_count": report_count,
            "avg_score": round(float(avg_score), 1) if avg_score else 0
        }
    })


# 修改密码
@auth.route("/change_password", methods=["POST"])
@jwt_required()
def change_password():
    uid = int(get_jwt_identity())
    data = request.json
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return error("参数缺失：旧密码/新密码不能为空")
    if len(new_password) < 6:
        return error("新密码长度不能少于6位")

    user = User.query.get(uid)
    if not check_password_hash(user.password, old_password):
        return error("旧密码错误")

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return success(msg="密码修改成功")
