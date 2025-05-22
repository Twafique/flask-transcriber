import os
import re
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import openai

app = Flask(__name__)

def extract_video_id(url):
    """
    Extracts the YouTube video ID from a URL.
    Returns video ID string or raises ValueError if invalid.
    """
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

        # Fetch transcript using youtube_transcript_api
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript_list])

        # Generate flashcards using OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this env var is set in Render
        
        prompt = (
            f"Generate 3 simple question-answer flashcards from the following transcript:\n\n{transcript_text}\n\n"
            "Format as a JSON list of objects with 'q' and 'a' keys."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        flashcards_text = response.choices[0].message.content

        # Try to parse flashcards JSON from response
        import json
        try:
            flashcards = json.loads(flashcards_text)
        except Exception:
            # fallback if parsing fails
            flashcards = [{"q": "Sample question?", "a": "Sample answer."}]

        return jsonify({
            "message": "Received URL and processed transcript",
            "video_url": video_url,
            "video_id": video_id,
            "flashcards": flashcards
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
