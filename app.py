import os
from flask import Flask, request, jsonify
import openai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_url = data.get('video_url')

    try:
        # Extract video ID
        video_id = parse_qs(urlparse(video_url).query).get("v")
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400
        video_id = video_id[0]

        # Fetch transcript in Hindi or English
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
        except Exception:
            # Try just English if Hindi+English fails
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

        # Combine transcript into one text block
        transcript_text = " ".join([t['text'] for t in transcript_list])

        # For now, we only return the transcript (OpenAI part comes next)
        return jsonify({
            "message": "Transcript fetched successfully",
            "video_url": video_url,
            "transcript": transcript_text[:300] + "..."  # Preview only
        })

    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video."}), 403
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/healthz')
def health_check():
    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
