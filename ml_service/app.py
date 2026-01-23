from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/status")
def status():
    return jsonify({"status": "ok", "service": "ml_service"})

if __name__ == "__main__":
    app.run(debug=True)
