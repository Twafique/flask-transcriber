import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_url = data.get('video_url')
    return jsonify({
        "message": "Received URL",
        "video_url": video_url,
        "flashcards": [
            {"q": "Sample question?", "a": "Sample answer."}
        ]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    @app.route('/healthz')
def health_check():
    return "OK", 200
