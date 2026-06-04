from Website import create_app
from flask import request

app = create_app()

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return app.make_default_options_response()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)