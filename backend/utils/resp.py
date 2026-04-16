from flask import jsonify


def success(data=None, msg="success"):
    return jsonify({"code": 200, "msg": msg, "data": data})


def error(msg="error", code=400):
    return jsonify({"code": code, "msg": msg, "data": None}), code
