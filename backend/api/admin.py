from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, QuestionBank, User, InterviewSession, Report
from utils.resp import success, error

admin = Blueprint("admin", __name__)


def admin_required(fn):
    """管理员权限装饰器"""
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error("权限不足，仅管理员可操作", 403)
        return fn(*args, **kwargs)
    return wrapper


# ========== 题库管理 ==========

# 查询题库（支持按岗位/难度筛选）
@admin.route("/questions", methods=["GET"])
@jwt_required()
@admin_required
def list_questions():
    position = request.args.get("position")
    difficulty = request.args.get("difficulty")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = QuestionBank.query
    if position:
        query = query.filter_by(position=position)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    pagination = query.order_by(QuestionBank.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    result = []
    for q in pagination.items:
        result.append({
            "id": q.id,
            "position": q.position,
            "difficulty": q.difficulty,
            "question": q.question,
            "q_type": q.q_type,
            "created_at": q.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return success({
        "list": result,
        "total": pagination.total,
        "page": page,
        "per_page": per_page
    })


# 新增题目
@admin.route("/questions", methods=["POST"])
@jwt_required()
@admin_required
def add_question():
    d = request.json
    position = d.get("position")
    question = d.get("question")
    if not position or not question:
        return error("参数缺失：岗位/题目不能为空")
    q = QuestionBank(
        position=position,
        difficulty=d.get("difficulty", "中等"),
        question=question,
        q_type=d.get("q_type", "技术题")
    )
    db.session.add(q)
    db.session.commit()
    return success(msg="题目添加成功")


# 批量导入题目
@admin.route("/questions/batch", methods=["POST"])
@jwt_required()
@admin_required
def batch_add_questions():
    d = request.json
    questions = d.get("questions", [])
    if not questions:
        return error("参数缺失：题目列表不能为空")
    count = 0
    for item in questions:
        if item.get("position") and item.get("question"):
            q = QuestionBank(
                position=item["position"],
                difficulty=item.get("difficulty", "中等"),
                question=item["question"],
                q_type=item.get("q_type", "技术题")
            )
            db.session.add(q)
            count += 1
    db.session.commit()
    return success(msg=f"成功导入{count}道题目")


# 删除题目
@admin.route("/questions/<int:qid>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_question(qid):
    q = QuestionBank.query.get(qid)
    if not q:
        return error("题目不存在")
    db.session.delete(q)
    db.session.commit()
    return success(msg="删除成功")


# 修改题目
@admin.route("/questions/<int:qid>", methods=["PUT"])
@jwt_required()
@admin_required
def update_question(qid):
    q = QuestionBank.query.get(qid)
    if not q:
        return error("题目不存在")
    d = request.json
    if d.get("position"):
        q.position = d["position"]
    if d.get("difficulty"):
        q.difficulty = d["difficulty"]
    if d.get("question"):
        q.question = d["question"]
    if d.get("q_type"):
        q.q_type = d["q_type"]
    db.session.commit()
    return success(msg="修改成功")


# ========== 用户管理 ==========

@admin.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    result = []
    for u in pagination.items:
        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
        })
    return success({
        "list": result,
        "total": pagination.total,
        "page": page,
        "per_page": per_page
    })


# ========== 数据统计 ==========

@admin.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
def stats():
    user_count = User.query.count()
    question_count = QuestionBank.query.count()
    session_count = InterviewSession.query.count()
    report_count = Report.query.count()
    return success({
        "user_count": user_count,
        "question_count": question_count,
        "session_count": session_count,
        "report_count": report_count
    })


# ========== 初始化题库种子数据 ==========

@admin.route("/seed", methods=["POST"])
@jwt_required()
@admin_required
def seed_questions():
    """初始化面试题库种子数据（至少两个岗位）"""
    seed_data = [
        # Java后端岗位
        {"position": "Java后端", "difficulty": "初级", "q_type": "技术题",
         "question": "请解释Java中的面向对象三大特性（封装、继承、多态），并各举一个实际应用场景。"},
        {"position": "Java后端", "difficulty": "初级", "q_type": "技术题",
         "question": "ArrayList和LinkedList的区别是什么？分别适用于什么场景？"},
        {"position": "Java后端", "difficulty": "中等", "q_type": "技术题",
         "question": "请解释Spring IoC和AOP的核心原理，以及在项目中的典型使用场景。"},
        {"position": "Java后端", "difficulty": "中等", "q_type": "技术题",
         "question": "MySQL中索引的底层数据结构是什么？为什么使用B+树而不是B树？"},
        {"position": "Java后端", "difficulty": "中等", "q_type": "场景题",
         "question": "如果一个接口响应时间从100ms突然变为5s，你会如何排查定位问题？"},
        {"position": "Java后端", "difficulty": "高级", "q_type": "技术题",
         "question": "请解释JVM的内存模型和垃圾回收机制，常见的GC算法有哪些？"},
        {"position": "Java后端", "difficulty": "高级", "q_type": "场景题",
         "question": "设计一个支持高并发的秒杀系统，需要考虑哪些关键技术点？"},
        {"position": "Java后端", "difficulty": "初级", "q_type": "项目经历",
         "question": "请介绍一个你做过的项目，你在其中负责什么模块？遇到了什么技术难题？"},
        {"position": "Java后端", "difficulty": "中等", "q_type": "行为题",
         "question": "描述一次你和团队成员产生技术分歧的经历，你是如何解决的？"},
        {"position": "Java后端", "difficulty": "高级", "q_type": "技术题",
         "question": "请解释分布式事务的常见解决方案（2PC、TCC、Saga），各自的优缺点是什么？"},

        # Web前端岗位
        {"position": "Web前端", "difficulty": "初级", "q_type": "技术题",
         "question": "请解释CSS盒模型，以及box-sizing的content-box和border-box的区别。"},
        {"position": "Web前端", "difficulty": "初级", "q_type": "技术题",
         "question": "JavaScript中var、let、const的区别是什么？什么是变量提升？"},
        {"position": "Web前端", "difficulty": "中等", "q_type": "技术题",
         "question": "请解释Vue的响应式原理，Vue2和Vue3在响应式实现上有什么区别？"},
        {"position": "Web前端", "difficulty": "中等", "q_type": "技术题",
         "question": "什么是虚拟DOM？它是如何提升页面渲染性能的？diff算法的核心思路是什么？"},
        {"position": "Web前端", "difficulty": "中等", "q_type": "场景题",
         "question": "一个页面加载速度很慢，你会从哪些方面进行性能优化？"},
        {"position": "Web前端", "difficulty": "高级", "q_type": "技术题",
         "question": "请解释浏览器的事件循环机制（Event Loop），宏任务和微任务的执行顺序是怎样的？"},
        {"position": "Web前端", "difficulty": "高级", "q_type": "场景题",
         "question": "如何设计一个前端微前端架构方案？需要解决哪些核心问题？"},
        {"position": "Web前端", "difficulty": "初级", "q_type": "项目经历",
         "question": "请介绍你做过的一个前端项目，使用了哪些技术栈？如何组织项目结构？"},
        {"position": "Web前端", "difficulty": "中等", "q_type": "行为题",
         "question": "你是如何持续学习前端新技术的？最近学习了什么新技术？"},
        {"position": "Web前端", "difficulty": "高级", "q_type": "技术题",
         "question": "请解释Webpack的构建流程和热更新原理，Vite相比Webpack有什么优势？"},

        # Python算法岗位
        {"position": "Python算法", "difficulty": "初级", "q_type": "技术题",
         "question": "Python中列表和元组的区别是什么？字典的底层实现原理是什么？"},
        {"position": "Python算法", "difficulty": "初级", "q_type": "技术题",
         "question": "请解释什么是过拟合和欠拟合，如何解决？"},
        {"position": "Python算法", "difficulty": "中等", "q_type": "技术题",
         "question": "请比较随机森林和XGBoost的优缺点，分别适用于什么场景？"},
        {"position": "Python算法", "difficulty": "中等", "q_type": "技术题",
         "question": "请解释CNN和RNN的区别，以及Transformer架构的核心机制（Self-Attention）。"},
        {"position": "Python算法", "difficulty": "中等", "q_type": "场景题",
         "question": "如何处理样本不均衡问题？你在项目中使用过哪些方法？"},
        {"position": "Python算法", "difficulty": "高级", "q_type": "技术题",
         "question": "请解释大语言模型的训练流程（预训练、SFT、RLHF），以及LoRA微调的原理。"},
        {"position": "Python算法", "difficulty": "高级", "q_type": "场景题",
         "question": "如何设计一个RAG（检索增强生成）系统？需要考虑哪些关键环节？"},
        {"position": "Python算法", "difficulty": "初级", "q_type": "项目经历",
         "question": "请介绍一个你做过的机器学习/深度学习项目，使用了什么模型和数据集？"},
        {"position": "Python算法", "difficulty": "中等", "q_type": "行为题",
         "question": "描述一次你的模型效果不达预期时，你是如何分析和改进的？"},
        {"position": "Python算法", "difficulty": "高级", "q_type": "技术题",
         "question": "请解释分布式训练的常见方案（数据并行、模型并行），以及DeepSpeed的核心优化策略。"},
    ]

    count = 0
    for item in seed_data:
        exists = QuestionBank.query.filter_by(
            position=item["position"],
            question=item["question"]
        ).first()
        if not exists:
            db.session.add(QuestionBank(**item))
            count += 1
    db.session.commit()
    return success(msg=f"种子数据导入成功，新增{count}道题目")
