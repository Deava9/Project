import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()


class Config:
    # Flask安全配置
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # 7天有效期

    # MySQL配置
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 豆包大模型配置
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-pro-4k")
    DOUBAO_API_URL = os.getenv("DOUBAO_API_URL")
