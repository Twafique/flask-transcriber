from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs

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

        # Fetch transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])

        # Combine into one string
        transcript_text = " ".join([t['text'] for t in transcript_list])

        # (In future) call OpenAI here

        return jsonify({
            "message": "Transcript fetched successfully",
            "video_url": video_url,
            "transcript": transcript_text[:300] + "..."  # Trimmed for readability
        })

    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video."}), 403
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
