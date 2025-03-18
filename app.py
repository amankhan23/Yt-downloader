from flask import Flask, request, render_template, jsonify, Response, stream_with_context
from yt_dlp import YoutubeDL
import requests
import os  # Import the os module

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    youtube_url = request.form.get("video_url")
    if not youtube_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Configure yt-dlp options
        ydl_opts = {
            "format": "best[ext=mp4]",
            "nocheckcertificate": True,
            "cookies-from-browser": "edge",  # Use cookies from Edge
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)  # Don't download yet
            video_url = info_dict["url"]  # Get the direct download URL
            filename = ydl.prepare_filename(info_dict)  # Get the suggested filename

        # Get the content length from the video URL
        with requests.get(video_url, stream=True, verify=False) as r:  # added verify=False
            r.raise_for_status()
            content_length = int(r.headers.get("Content-Length", 0))

        # Stream the video from the backend to the frontend
        def generate():
            with requests.get(video_url, stream=True, verify=False) as r:  # added verify=False
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

        # Return the streamed response with headers
        return Response(
            stream_with_context(generate()),
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "video/mp4",
                "Content-Length": str(content_length),  # Include Content-Length header
            },
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ != "__main__":  # important change
    server = app  # changed from app.run