import streamlit as st

import json
import os
from time import strftime
from time import gmtime
import codecs
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from youtube_downloader import download_youtube_video
from ffvideo import run_ffmpeg_with_progress, get_file_extension

def show_srt(filename):
    server_ocr = 'http://127.0.0.1:5000/'
    response = requests.get(server_ocr + filename)

    if response.status_code == 200:
        srt_content = response.text
        return srt_content
    else:
        return False

def upload_file(filename, upload_folder):

    file_source = os.path.join(upload_folder, filename.name)

    os.makedirs(upload_folder, exist_ok=True)

    with open(file_source, 'wb') as out:
        out.write(filename.getbuffer())

    out.close()

    return file_source

def send_file_to_server(file_path, lang, gpu, sim, conf, start_time, end_time, skip_frame, brightness_threshold):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    url = "http://127.0.0.1:5000/upload"

    data = {
        "lang": lang,
        "gpu": gpu,
        "sim": sim,
        "conf": conf,
        "start_time": start_time,
        "end_time": end_time,
        "skip_frame": skip_frame,
        "brightness_threshold": brightness_threshold
    }

    with open(file_path, "rb") as file:
        files = {"file": (file_path, file)}
        print(files)
        response = session.post(url, data=data, files=files)

    return json.loads(response.text)


def main():
    st.title('Extract hardcoded subtitles from video')

    st.subheader('Choose your options :')

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Choose a file")
    with col2:
        video_yt = st.text_input('Or Enter Youtube URL')

    st.write("---")

    cropping = st.checkbox('Enabled video cropping for better result when processing ocr. it takes longer !')

    if uploaded_file or video_yt:
        UPLOAD_FOLDER = 'uploads'
        if uploaded_file :
            file_source = upload_file(uploaded_file, UPLOAD_FOLDER)
        elif video_yt:
            file_source = download_youtube_video(video_yt)

        print(file_source)



        #max_time = str(strftime("%M:%S", gmtime(duration))).replace(".", ":")

        col1, col2 = st.columns(2)

        with col1:
            gpu = st.radio(
                "Use GPU",
                ["True", "False"]
            )
        with col2:
            lang = st.selectbox(
                'choose a language',
                ('ch', 'en', 'korean', 'japan', 'latin'))

        col4, col5 = st.columns(2)
        with col4:
            start_time = st.text_input('Time start', placeholder="0:00")

        with col5:
            end_time = st.text_input('Time end', placeholder='max_time')

        col6, col7 = st.columns(2)

        with col6:
            conf = st.number_input('Confidence threshold for word predictions', step=1, value=80)

        with col7:
            sim = st.number_input('Similarity threshold for subtitle lines', step=1, value=50)

        col8, col9 = st.columns(2)

        with col8:
            skip_frame = st.radio(
                "Skip frame (speed increase)",
                ["True", "False"]
            )

        with col9:
            brightness_threshold = st.number_input('Brightness Threshold', step=1, value=1)

        st.write("---")

        if st.button('Generate Now'):
            with st.spinner('Wait for it...'):

                start_time = '0:00' if len(start_time) == 0 else start_time
                gpu = json.loads(gpu.lower())
                skip_frame = 1 if skip_frame == 'True' else 0

                if cropping:
                    run_ffmpeg_with_progress(UPLOAD_FOLDER, file_source)
                    st.info('video cropped successfully, OCR will start...', icon="ℹ️")
                    extension = get_file_extension(file_source)
                    file_source = os.path.join(UPLOAD_FOLDER, Path(file_source).stem + '_cropped' + extension)

                ocr_server = send_file_to_server(file_source, lang, gpu, int(sim), int(conf), start_time, end_time, skip_frame, brightness_threshold)

                file_srt = ocr_server['output']

                if not show_srt(file_srt):
                    st.warning('no subtitles found', icon="⚠️")
                else:
                    tab1, tab2 = st.tabs(["Subtitle", "original video"])

                    with tab1:
                        st.code(show_srt(file_srt), language="plaintext")
                    with tab2:
                        video_file = open(file_source, 'rb')
                        video_bytes = video_file.read()

                        st.video(video_bytes)

                    st.download_button(
                        label="Download srt file",
                        data=show_srt(file_srt),
                        file_name=file_srt,
                        mime='text/plain',
                    )


if __name__ == '__main__':
    main()
