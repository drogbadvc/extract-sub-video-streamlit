from videocr import save_subtitles_to_file
import os.path
from os import path


def get_file_extension(file_path):
    file_name = os.path.basename(file_path)  # Get the base file name
    file_extension = os.path.splitext(file_name)[1]  # Get the file extension
    return file_extension


def run_ocr_with_progress(filename, output_name, lang, gpu, sim, conf, start_time, end_time, skip_frame, brightness_threshold):
    if path.exists(filename):
        save_subtitles_to_file(filename,
                               output_name,
                               lang=lang, time_start=start_time, time_end=end_time,
                               sim_threshold=sim, conf_threshold=conf, use_fullframe=False, use_gpu=gpu,
                               brightness_threshold=brightness_threshold, similar_image_threshold=1000,
                               frames_to_skip=skip_frame)
