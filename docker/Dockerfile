FROM balenalib/raspberrypi3:bullseye-20240227

ENV QEMU_CPU=max
ENV DEBIAN_FRONTEND=noninteractive

RUN install_packages \
 build-essential \
 libraspberrypi0 \
 procps \
 sudo \
 wget \
 unzip \
 xz-utils \
 ffmpeg \
 portaudio19-dev \
 python3 \
 python3-pip \
 python3-dev \
 libopenjp2-7-dev \
 libtiff5 \
 libatlas-base-dev \
 libhdf5-dev \
 alsa-utils \
 espeak
RUN install_packages \
 libharfbuzz-bin \
 libwebp6 \
 libjasper1 \
 libilmbase25 \
 libgstreamer1.0-0 \
 libavcodec-extra58 \
 libavformat58
RUN install_packages \
 libopencv-dev \
 zbar-tools \
 libzbar0 \
 sox \
 libsox-fmt-all \
 libopenblas-dev
RUN install_packages \
 avrdude \
 tesseract-ocr \
 tesseract-ocr-eng \
 tesseract-ocr-ita \
 tesseract-ocr-fra \
 tesseract-ocr-spa \
 tesseract-ocr-deu

ENV READTHEDOCS=True
ADD requirements.txt /tmp/.
RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /coderbot && \
mkdir -p /coderbot/data && \
mkdir -p /coderbot/logs && \
mkdir -p /coderbot/cnn_modules && \
mkdir -p /coderbot/coderbot && \
mkdir -p /coderbot/defaults && \
mkdir -p /coderbot/sounds

ADD coderbot /coderbot/coderbot/.
ADD defaults /coderbot/defaults/.
ADD sounds /coderbot/sounds/.

ADD docker/scripts/*.sh /tmp/.
RUN /tmp/install_generic_cnn_models.sh
RUN /tmp/install_lib_firmware.sh
ADD docker/start.sh /coderbot/.

ARG CODERBOT_VERSION
ENV CODERBOT_VERSION=${CODERBOT_VERSION}

ENTRYPOINT /coderbot/start.sh
