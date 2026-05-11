from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import timedelta
import os

db = SQLAlchemy()
mail = Mail()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)

    # JWT config
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "samba-super-secret-jwt-key-32chars!")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # CORS
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": [
            "http://localhost:5173",
            "https://stop-the-cap.vercel.app",
            "https://stop-the-cap-vlxv-gxebgegof-reuben-40s-projects.vercel.app"
        ]}},
        allow_headers=["Content-Type", "Authorization"]
    )

    # DB setup
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, DB_NAME)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Mail config — Brevo SMTP
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "samba16@123")
    app.config["MAIL_SERVER"] = "smtp-relay.brevo.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "aaa675001@smtp-brevo.com")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = ("Samba Health Outreach", "sambahomehealthcare@gmail.com")

    # Init extensions
    db.init_app(app)
    mail.init_app(app)
    JWTManager(app)

    # Blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app