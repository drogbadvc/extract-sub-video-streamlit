# Version: 2.0.0
FROM registry.baidubce.com/paddlepaddle/paddle:2.0.0-gpu-cuda10.1-cudnn7

WORKDIR paddle

# PaddleOCR base on Python3.7
RUN pip3.7 install --upgrade pip -i https://mirror.baidu.com/pypi/simple

RUN python3.7 -m pip install paddlepaddle-gpu==2.0.0 -i https://mirror.baidu.com/pypi/simple

RUN git clone https://gitee.com/paddlepaddle/PaddleOCR

RUN cd PaddleOCR && pip3.7 install -r requirements.txt

# Change working directory to /videocr
WORKDIR /home

# Install videocr-PaddleOCR from GitHub repository
RUN git clone https://github.com/oliverfei/videocr-PaddleOCR.git

RUN mv videocr-PaddleOCR videocr

WORKDIR /home/videocr

RUN python3.7 -m pip install .

# Copiez les fichiers du dossier app local vers le répertoire de travail du conteneur
COPY ./videocr /home/videocr

# Exposez le port sur lequel votre application sera accessible
EXPOSE 5000

# Lancez l'application
CMD ["python3.7", "/home/videocr/app.py"]
