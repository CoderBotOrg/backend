FROM debian:bullseye-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -y \
 patch \
 procps \
 sudo \
 wget \
 unzip \
 xz-utils \
 ffmpeg \
 portaudio19-dev \
 python3 \
 python3-pip \
 libopenjp2-7-dev \
 libtiff5 \
 libatlas-base-dev \
 libhdf5-dev \
 alsa-utils \
 espeak \
 libharfbuzz-bin \
 libwebp6 \
 libilmbase25 \
 libgstreamer1.0-0 \
 libavcodec-extra58 \
 libavformat58 \
 libopencv-dev \
 zbar-tools \
 libzbar0 \
 sox \
 libsox-fmt-all \
 libopenblas-dev \
 avrdude \
 tesseract-ocr \
 tesseract-ocr-eng \
 tesseract-ocr-ita \
 tesseract-ocr-fra \
 tesseract-ocr-spa \
 tesseract-ocr-deu

ADD docker/stub/requirements.txt /tmp/.
RUN pip install --upgrade pip && \
 pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /coderbot && \
mkdir -p /coderbot/data && \
mkdir -p /coderbot/logs && \
mkdir -p /coderbot/updatePackages && \
mkdir -p /coderbot/cnn_modules && \
mkdir -p /coderbot/coderbot && \
mkdir -p /coderbot/defaults && \
mkdir -p /coderbot/sounds

ADD coderbot /coderbot/coderbot/.
ADD stub /coderbot/stub/.
ADD test /coderbot/test/.
ADD defaults /coderbot/defaults/.
ADD sounds /coderbot/sounds/.

ADD docker/scripts/*.sh /tmp/.
RUN /tmp/install_generic_cnn_models.sh
ADD docker/stub/start.sh /coderbot/.

ARG CODERBOT_VERSION
ENV CODERBOT_VERSION=${CODERBOT_VERSION}

ENTRYPOINT /coderbot/start.sh
