import os
from pytube import YouTube

def download_youtube_video(url, output_directory="uploads"):
    os.makedirs(output_directory, exist_ok=True)

    yt = YouTube(url)

    video = yt.streams.get_highest_resolution()

    video.download(output_directory)

    downloaded_filename = os.path.join(output_directory, video.default_filename)

    return downloaded_filename

