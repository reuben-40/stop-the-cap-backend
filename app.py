from flask import Flask, jsonify, request
from flask_cors import CORS
from Website import create_app

app = create_app()


app.secret_key = "samba16@123"

# Enable CORS for frontend (React/Vite)
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

    # Basic validation (replace with DB later)
    if not all([email, password, first_name, second_name, contact_number]):
        return jsonify({"status": "Missing fields"}), 400

    # Fake success response (replace with database logic)
    return jsonify({
        "status": "SignUp successful",
        "user": {
            "email": email,
            "firstName": first_name,
            "secondName": second_name,
            "contactNumber": contact_number
        }
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)