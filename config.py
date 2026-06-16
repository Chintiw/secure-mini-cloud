# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env if present; silent no-op if file is absent

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Security — loaded from .env; falls back to a random key only for CI/testing.
    # WARNING: A random fallback means sessions are lost on restart.
    # Always set SECRET_KEY in .env for any real usage.
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'secure_cloud.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload limits
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024          # 50 MB (FILE-03)
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'jpg', 'png', 'zip'}
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Active config — override by setting APP_ENV=production in .env
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
}
active_config = config_map.get(os.environ.get('APP_ENV', 'development'), DevelopmentConfig)
