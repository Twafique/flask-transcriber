import os
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googletrans import Translator
import openai
import re

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
        return " ".join([entry['text'] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

def translate_to_english(text):
    translator = Translator()
    translated = translator.translate(text, src='hi', dest='en')
    return translated.text

def generate_flashcards(text):
    prompt = f"""Generate 5 flashcards from the following text. Each flashcard should have a question and an answer:
    
{text}

Format:
[
  {{ "q": "...", "a": "..." }},
  ...
]
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return eval(response['choices'][0]['message']['content'])

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_url = data.get('video_url')
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    raw_transcript = get_transcript(video_id)
    if not raw_transcript:
        return jsonify({"error": "Transcript not found"}), 404

    translated = translate_to_english(raw_transcript)
    flashcards = generate_flashcards(translated)

    return jsonify({
        "message": "Flashcards generated",
        "video_url": video_url,
        "flashcards": flashcards
    })

@app.route('/healthz')
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
