from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.interview_service import interview_service
from models.models import db, Report, InterviewSession
from utils.resp import success, error
import json

rp = Blueprint("report", __name__)


# 生成面试报告
@rp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    uid = int(get_jwt_identity())
    d = request.json
    session_id = d.get("session_id")
    if not session_id:
        return error("参数缺失：会话ID不能为空")

    result, err = interview_service.gen_report(session_id, uid)
    if err:
        return error(err)
    return success(result)


# 查看单次面试报告
@rp.route("/detail/<session_id>", methods=["GET"])
@jwt_required()
def detail(session_id):
    report = Report.query.filter_by(session_id=session_id).first()
    if not report:
        return error("报告不存在，请先生成报告")
    return success({
        "session_id": report.session_id,
        "position": report.position,
        "score": report.score,
        "feedback": report.feedback,
        "radar_scores": json.loads(report.radar_scores) if report.radar_scores else {},
        "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })


# 查看用户所有面试报告
@rp.route("/list", methods=["GET"])
@jwt_required()
def report_list():
    uid = int(get_jwt_identity())
    position = request.args.get("position")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Report.query.filter_by(user_id=uid)
    if position:
        query = query.filter_by(position=position)

    pagination = query.order_by(
        Report.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    result = []
    for r in pagination.items:
        result.append({
            "id": r.id,
            "session_id": r.session_id,
            "position": r.position,
            "score": r.score,
            "feedback": r.feedback,
            "radar_scores": json.loads(r.radar_scores) if r.radar_scores else {},
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return success({
        "list": result,
        "total": pagination.total,
        "page": page,
        "per_page": per_page
    })


# 成长曲线 — 得分趋势
@rp.route("/trend", methods=["GET"])
@jwt_required()
def score_trend():
    uid = int(get_jwt_identity())
    position = request.args.get("position")
    result = interview_service.get_score_trend(uid, position)
    return success(result)


# 个性化提升建议
@rp.route("/improvement", methods=["POST"])
@jwt_required()
def improvement():
    uid = int(get_jwt_identity())
    d = request.json
    position = d.get("position")
    if not position:
        return error("参数缺失：岗位不能为空")
    result, err = interview_service.get_improvement_advice(uid, position)
    if err:
        return error(err)
    return success(result)
