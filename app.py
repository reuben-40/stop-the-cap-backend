from flask import Flask, jsonify, request
from flask_cors import CORS
from Website import create_app
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from Website.models import Appointment, db  # ✅ ensure db is imported

app = create_app()

#  SECRET KEY
app.config["SECRET_KEY"] = "samba16@123"
app.config["JWT_SECRET_KEY"] = "super-secret-jwt-key"  # REQUIRED for JWT

#  INIT JWT
jwt = JWTManager(app)

#  ENABLE CORS
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://192.168.100.8:5173",
        "http://192.168.100.8:8080",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
)


@app.route('/api/message', methods=['GET'])
def get_message():
    return jsonify({"message": "Hello from backend!"})


#  SIGNUP (still mock)
@app.route('/api/signUp', methods=['POST'])
def sign_up():
    data = request.get_json()

    if not data:
        return jsonify({"status": "No JSON received"}), 400

    email = data.get("email")
    password = data.get("password")
    first_name = data.get("firstName")
    second_name = data.get("secondName")
    contact_number = data.get("contactNumber")

    if not all([email, password, first_name, second_name, contact_number]):
        return jsonify({"status": "Missing fields"}), 400

    return jsonify({
        "status": "SignUp successful",
        "user": {
            "email": email,
            "firstName": first_name,
            "secondName": second_name,
            "contactNumber": contact_number
        }
    })


#  LOGIN (YOU NEED THIS FOR TOKENS)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # ⚠️ Replace with DB check
    if not email or not password:
        return jsonify({"message": "Invalid credentials"}), 401

    # 👉 create token (use user_id ideally)
    access_token = create_access_token(identity=email)

    return jsonify({
        "token": access_token
    })


#  GET APPOINTMENTS
@app.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():
    user_id = get_jwt_identity()

    appointments = Appointment.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": a.id,
            "date": a.date,
            "day": a.day,
            "time": a.time
        } for a in appointments
    ])


#  CREATE APPOINTMENT (FIXED - YOU WERE MISSING THIS)
@app.route("/appointments", methods=["POST"])
@jwt_required()
def create_appointment():
    user_id = get_jwt_identity()
    data = request.get_json()

    new_appointment = Appointment(
        date=data.get("date"),
        day=data.get("day"),
        time=data.get("time"),
        user_id=user_id
    )

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({"message": "Appointment created"}), 201





@app.route("/appointments/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(id):
    user_id = get_jwt_identity()

    appointment = Appointment.query.filter_by(id=id, user_id=user_id).first()
    
    if not appointment:
        return jsonify({"message": "Appointment not found."}), 404
    
    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment cancelled successfully."}), 200




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)