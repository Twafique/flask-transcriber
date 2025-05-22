import os
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_video_id(url):
    """
    Extracts the YouTube video ID from a URL.
    Returns video ID string or raises ValueError if invalid.
    """
    # Regex pattern to capture video ID from different YouTube URL formats
    pattern = (
        r'(?:https?://)?(?:www\.)?'
        r'(?:youtube\.com/watch\?v=|youtu\.be/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.get_json()
        if not data or 'video_url' not in data:
            return jsonify({"error": "Missing 'video_url' in request body"}), 400

        video_url = data['video_url']
        video_id = extract_video_id(video_url)

        # Here you can add your logic to process the video_id, call APIs, etc.
        # For now, returning sample flashcards:

        return jsonify({
            "message": "Received URL",
            "video_url": video_url,
            "video_id": video_id,
            "flashcards": [
                {"q": "Sample question?", "a": "Sample answer."}
            ]
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
