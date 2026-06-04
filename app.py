from Website import create_app
from flask import request
from Website import db

app = create_app()

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return app.make_default_options_response()

# ── Temporary reset route ─────────────────────────────────────────────────────
@app.route("/reset-db")
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    return "Database reset successfully!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)