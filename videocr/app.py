from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path

from ocrvideo import run_ocr_with_progress, get_file_extension

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mkv', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part in the request", 400

        file = request.files['file']

        if file.filename == '':
            return "No file selected for uploading", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            name_origin = Path(file_path_name).stem
            output_ext = name_origin + '.srt'
            output = os.path.join(app.config['UPLOAD_FOLDER'], output_ext)

            lang = request.form.get('lang', default=None)
            gpu = request.form.get('gpu', default=None)
            gpu = json.loads(gpu.lower())
            sim = request.form.get('sim', default=None)
            conf = request.form.get('conf', default=None)
            start_time = request.form.get('start_time', default=None)
            end_time = request.form.get('end_time', default=None)
            skip_frame = request.form.get('skip_frame', default=None)
            brightness_threshold = request.form.get('brightness_threshold', default=None)

            run_ocr_with_progress(file_path_name, output, lang, gpu, float(sim),
                                  float(conf), start_time, end_time,
                                  int(skip_frame), float(brightness_threshold))

            return jsonify({
                "message": f"File uploaded and saved. OCR processing started.",
                "output": 'output/'+ output_ext,
                "lang": lang,
                "gpu": gpu,
                "sim": sim,
                "conf": conf,
                "start_time": start_time,
                "end_time": end_time,
                "skip_frame": skip_frame,
                "brightness_threshold": brightness_threshold
            }), 200
        else:
            return jsonify({
                "message": "File type not allowed"}), 400


@app.route('/output/<filename>', methods=['GET'])
def display_txt_output(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(filepath):
        with open(filepath, 'r') as txt_file:
            content = txt_file.read()
            return content
    else:
        return "File not found", 404


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
