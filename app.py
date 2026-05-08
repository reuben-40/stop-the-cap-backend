from flask import Flask, jsonify, request
from flask_mail import Mail, Message
from flask_cors import CORS
from Website import create_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from Website.models import Appointment, User, db

app = create_app()

# Mail config only — JWT and CORS are handled inside create_app()
app.config["SECRET_KEY"] = "samba16@123"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "sambahomehealthcare@gmail.com"
app.config["MAIL_PASSWORD"] = "iqih sovm lkoc txfu"
app.config["MAIL_DEFAULT_SENDER"] = "sambahomehealthcare@gmail.com"

mail = Mail(app)


def send_appointment_email(client_email, client_name, date, day, time):
    subject = "Your Virtual Appointment Confirmation – Samba Health Outreach"

    body = f"""
Hello {client_name},

Your virtual appointment has been successfully booked! Here are your details:

  Date : {date}
  Day  : {day}
  Time : {time}

The link to your virtual meeting will be shared with you on the day of the appointment.
If you need to reschedule or cancel, please make the changes before the day of the appointment.

Thank you for choosing our services!

Best regards,
Samba Health Outreach
"""
    msg = Message(subject=subject, recipients=[client_email], body=body)
    mail.send(msg)


@app.route('/api/message', methods=['GET'])
def get_message():
    return jsonify({"message": "Hello from backend!"})


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


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Invalid credentials"}), 401

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "No account found with that email."}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "access_token": access_token,
        "message": "Login successful"
    })


@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    print(f"DEBUG /api/me → user_id: {user_id}")
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "firstName": user.first_name,
    })


@app.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():
    user_id = int(get_jwt_identity())

    appointments = Appointment.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": a.id,
            "date": a.date,
            "day": a.day,
            "time": a.time
        } for a in appointments
    ])


@app.route("/appointments", methods=["POST"])
@jwt_required()
def create_appointment():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    date = data.get("date")
    day = data.get("day")
    time = data.get("time")

    new_appointment = Appointment(
        date=date,
        day=day,
        time=time,
        user_id=user_id
    )

    db.session.add(new_appointment)
    db.session.commit()

    user = User.query.get(user_id)
    print(f"DEBUG → user_id from token: {user_id} | user found: {user}")

    email_sent = False
    if user:
        try:
            send_appointment_email(
                client_email=user.email,
                client_name=user.first_name,
                date=date,
                day=day,
                time=time
            )
            email_sent = True
            print(f"✅ Email sent successfully to {user.email}")
        except Exception as e:
            print(f"❌ Email error: {e}")
    else:
        print(f"❌ No user found for id: {user_id}")

    return jsonify({
        "message": "Appointment booked successfully",
        "email_sent": email_sent
    }), 201


@app.route("/appointments/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(id):
    user_id = int(get_jwt_identity())

    appointment = Appointment.query.filter_by(id=id, user_id=user_id).first()

    if not appointment:
        return jsonify({"message": "Appointment not found."}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment cancelled successfully."}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)