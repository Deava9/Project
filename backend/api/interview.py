from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.interview_service import interview_service
from utils.resp import success, error

iv = Blueprint("interview", __name__)


# 获取可选岗位列表
@iv.route("/positions", methods=["GET"])
@jwt_required()
def positions():
    result = interview_service.get_positions()
    return success(result)


# 启动面试
@iv.route("/start", methods=["POST"])
@jwt_required()
def start():
    uid = int(get_jwt_identity())
    d = request.json
    position = d.get("position")
    difficulty = d.get("difficulty")
    if not position or not difficulty:
        return error("参数缺失：岗位/难度不能为空")
    sid, q = interview_service.start(uid, position, difficulty)
    return success({"session_id": sid, "question": q})


# 面试对话
@iv.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    d = request.json
    sid = d.get("session_id")
    msg = d.get("message")
    if not sid or not msg:
        return error("参数缺失：会话ID/消息不能为空")
    result, err = interview_service.chat(sid, int(get_jwt_identity()), msg)
    if err:
        return error(err)
    return success(result)


# 手动结束面试
@iv.route("/end", methods=["POST"])
@jwt_required()
def end():
    d = request.json
    sid = d.get("session_id")
    if not sid:
        return error("参数缺失：会话ID不能为空")
    result, err = interview_service.end_interview(sid, int(get_jwt_identity()))
    if err:
        return error(err)
    return success(result, msg="面试已结束")


# 获取面试历史记录
@iv.route("/history", methods=["GET"])
@jwt_required()
def history():
    from models.models import InterviewSession
    uid = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    position = request.args.get("position")

    query = InterviewSession.query.filter_by(user_id=uid)
    if position:
        query = query.filter_by(position=position)

    pagination = query.order_by(
        InterviewSession.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    result = []
    for s in pagination.items:
        result.append({
            "session_id": s.id,
            "position": s.position,
            "difficulty": s.difficulty,
            "round_count": s.round_count,
            "status": s.status,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return success({
        "list": result,
        "total": pagination.total,
        "page": page,
        "per_page": per_page
    })


# 获取某次面试的对话记录
@iv.route("/messages/<session_id>", methods=["GET"])
@jwt_required()
def messages(session_id):
    from models.models import ChatMessage, InterviewSession
    sess = InterviewSession.query.get(session_id)
    if not sess:
        return error("会话不存在")
    msgs = ChatMessage.query.filter_by(session_id=session_id).order_by(
        ChatMessage.id
    ).all()
    result = []
    for m in msgs:
        result.append({
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return success({
        "messages": result,
        "session_info": {
            "position": sess.position,
            "difficulty": sess.difficulty,
            "round_count": sess.round_count,
            "status": sess.status,
            "created_at": sess.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    })
