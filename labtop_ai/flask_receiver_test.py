from flask import Flask, request, jsonify

app = Flask(__name__)

latest_data = {}


@app.route("/")
def home():
    return "Focus Collapse Flask Receiver is running."


@app.route("/update_state", methods=["POST"])
def update_state():
    global latest_data

    data = request.get_json()

    if data is None:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    latest_data = data

    print("[RECEIVED]", data)

    return jsonify({"status": "success", "received": data})


@app.route("/latest", methods=["GET"])
def latest():
    return jsonify(latest_data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
