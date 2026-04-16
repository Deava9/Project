from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# 用户表
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default="user")  # user/admin
    created_at = db.Column(db.DateTime, default=datetime.now)


# 面试题库表
class QuestionBank(db.Model):
    __tablename__ = "question_bank"
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20))
    question = db.Column(db.Text, nullable=False)
    q_type = db.Column(db.String(20))  # 技术题/场景题/行为题/项目经历
    created_at = db.Column(db.DateTime, default=datetime.now)


# 面试会话表
class InterviewSession(db.Model):
    __tablename__ = "interview_session"
    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer)
    position = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    round_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="ongoing")  # ongoing/finished
    created_at = db.Column(db.DateTime, default=datetime.now)


# 聊天消息表
class ChatMessage(db.Model):
    __tablename__ = "chat_message"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), index=True)
    role = db.Column(db.String(20))  # user/assistant/system
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)


# 面试报告表
class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    position = db.Column(db.String(50))
    score = db.Column(db.Integer)  # 0-100
    feedback = db.Column(db.Text)
    radar_scores = db.Column(db.Text)  # JSON字符串，六维评分
    created_at = db.Column(db.DateTime, default=datetime.now)
