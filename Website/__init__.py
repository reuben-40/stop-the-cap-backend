from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)

    # 🔐 JWT CONFIG
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "Samba16@123")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # 🔥 CORS CONFIG
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": [
            "http://192.168.100.8:5000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]}},
        allow_headers=["Content-Type", "Authorization"]
    )

    # 🗄️ DB SETUP
    os.makedirs(app.instance_path, exist_ok=True)

    db_path = os.path.join(app.instance_path, DB_NAME)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 🔌 INIT EXTENSIONS
    db.init_app(app)
    JWTManager(app)

    # 📦 BLUEPRINTS
    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app