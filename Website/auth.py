from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from .models import User, Appointment
from . import db

auth = Blueprint("auth", __name__)


# ── auth routes ───────────────────────────────────────────────────────────────

@auth.route("/api/sign-up", methods=["POST"])
def sign_up():
    data = request.get_json()

    first_name     = data.get("firstName")
    second_name    = data.get("secondName")
    email          = data.get("email")
    contact_number = data.get("contactNumber")
    password       = data.get("password")

    if not all([first_name, second_name, email, contact_number, password]):
        return jsonify({"status": "Please fill in all fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "User with this email already exists"}), 400

    new_user = User(
        first_name=first_name,
        second_name=second_name,
        email=email,
        contact_number=contact_number,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    access_token  = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return jsonify({
        "status": "success",
        "message": "Account created successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": new_user.id,
            "firstName": new_user.first_name,
            "email": new_user.email
        }
    }), 201


@auth.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email    = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "Please enter email and password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"status": "User not found"}), 404

    if not check_password_hash(user.password, password):
        return jsonify({"status": "Invalid credentials"}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "status": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "firstName": user.first_name,
            "email": user.email
        }
    }), 200


@auth.route("/api/logout", methods=["POST"])
def logout():
    # Stateless — the client simply discards both tokens.
    # Add a blocklist here if you need server-side revocation.
    return jsonify({"status": "Logged out successfully"}), 200


# Generates a new access token using the refresh token
@auth.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity     = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


# ── protected routes ──────────────────────────────────────────────────────────

@auth.route("/appointments", methods=["POST"])
@jwt_required()
def create_appointment():
    data = request.get_json()

    if not data.get("date") or not data.get("day") or not data.get("time"):
        return jsonify({"message": "Please fill all fields"}), 400

    user_id = int(get_jwt_identity())

    new_appointment = Appointment(
        date=data["date"],
        day=data["day"],
        time=data["time"],
        user_id=user_id
    )
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({"message": "Appointment booked successfully"}), 201


@auth.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():
    user_id      = int(get_jwt_identity())
    appointments = Appointment.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": a.id,
            "date": a.date,
            "day": a.day,
            "time": a.time,
            "user": {
                "id": a.user.id,
                "first_name": a.user.first_name,
                "email": a.user.email
            }
        }
        for a in appointments
    ]), 200


@auth.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = User.query.get(user_id)

    if not user:
        return jsonify({"loggedIn": False}), 401

    return jsonify({
        "loggedIn": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "firstName": user.first_name
        }
    }), 200