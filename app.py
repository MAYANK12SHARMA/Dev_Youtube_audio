import os
import logging
import tempfile
import gradio as gr
from yt_dlp import YoutubeDL
from PIL import Image
import requests
from io import BytesIO

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def download_audio(youtube_url: str):
    """Function to download YouTube video, convert it to MP3, and get the thumbnail"""
    try:
        # Check if the YouTube URL is valid
        if 'youtube.com' in youtube_url or 'youtu.be' in youtube_url:
            # Set yt-dlp options for downloading the best quality audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),  # Use temporary folder
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }

            # Download the video and convert to MP3
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                video_title = info_dict.get('title', 'Unknown Title')
                thumbnail_url = info_dict.get('thumbnail')
                
                # Download and convert the audio
                info_dict = ydl.extract_info(youtube_url, download=True)
                mp3_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            # Fetch thumbnail image from the YouTube video
            thumbnail_image = None
            if thumbnail_url:
                response = requests.get(thumbnail_url)
                thumbnail_image = Image.open(BytesIO(response.content))

            # Return the MP3 file path, thumbnail, and title
            return mp3_file_path, thumbnail_image, video_title

        else:
            return None, None, "Invalid YouTube link."

    except Exception as e:
        logging.error(f"Error processing YouTube link: {e}")
        return None, None, "Error processing YouTube link. Please try again."

def process_youtube_link(youtube_url):
    # Process the YouTube link and return the MP3 file, thumbnail, and title
    mp3_file_path, thumbnail_image, video_title = download_audio(youtube_url)
    
    if mp3_file_path:
        # Provide download option
        return f"Download MP3: {video_title}", mp3_file_path, thumbnail_image
    else:
        return "Error occurred. Please try again.", None, None

# Enhanced Gradio Interface with Predefined Image/Text
def gradio_interface(youtube_url):
    message, mp3_file_path, thumbnail_image = process_youtube_link(youtube_url)
    
    return message, mp3_file_path, thumbnail_image

# Custom CSS for enhanced visuals
css = """
body {
    background-color: #f0f4f8;
}

.gr-description{
    height: 100px;
}
h1 {
    color: #333;
    font-family: 'Arial', sans-serif;
    text-align: center;
}
.gr-button {
    background-color: #1db954 !important;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 12px;
}
.gr-button:hover {
    background-color: #1ed760 !important;
}
.gr-input {
    font-family: 'Arial', sans-serif;
    font-size: 16px;
    padding: 10px;
    width: 100%;
    border-radius: 8px;
    border: 1px solid #ccc;
    height: 300px;
}
.gr-output-text {
    font-size: 18px;
    color: #1db954;
}
.gr-output-file {
    font-size: 16px;
    color: #000;
}
footer {
    text-align: center;
    margin-top: 20px;
    font-family: 'Arial', sans-serif;
}
"""

# Predefined image and text before user input
default_image = "image.png"
default_text = "Please enter a YouTube link to get started!"

# Build the Gradio interface
with gr.Blocks(css=css) as app:
    gr.Markdown("# 🎵 YouTube to MP3 Converter with Thumbnail")
    gr.Markdown("**Enter a YouTube video link below, and you'll receive the MP3 audio with the video thumbnail for download!**")
    with gr.Row():
        with gr.Column():
            youtube_url_input = gr.Textbox(
                label="Enter YouTube Link", 
                placeholder="https://www.youtube.com/watch?v=example",
                elem_classes="gr-input"
            )
            submit_btn = gr.Button("Convert to MP3", elem_classes="gr-button")
        with gr.Column():
            thumbnail_display = gr.Image(value=default_image, label="Video Thumbnail", elem_classes="gr-output-image")
    
    mp3_message = gr.Textbox(value=default_text, label="Message", elem_classes="gr-output-text")
    mp3_download = gr.File(label="Download MP3", elem_classes="gr-output-file")

    # Link button to the function
    submit_btn.click(gradio_interface, inputs=youtube_url_input, outputs=[mp3_message, mp3_download, thumbnail_display])

    gr.Markdown("<footer>Made with ❤️ using Gradio | © 2024</footer>")

# Launch the Gradio app
if __name__ == "__main__":
    app.launch(server_port=8000, server_name="0.0.0.0")
