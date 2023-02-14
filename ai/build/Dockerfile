#-*- encoding: utf-8 -*-

# 可搬型病虫害識別装置
# 識別AI・Web API イメージ

FROM debian:bullseye

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Asia/Tokyo

# Apache のインストール
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ \
        > /etc/timezone
RUN apt update && \
    apt install --yes \
        apache2 \
        apache2-utils \
        ssl-cert \
        libapache2-mod-wsgi-py3 \
        libgtk2.0-dev \
        pkg-config

# Python とライブラリのインストール
#   Pillow: zlib1g-dev, libopenjp2-7
#   tflite-runtime: libatlas-base-dev (NumPy dependency)
RUN apt-get install --yes \
        python3 \
        python3-pip \
        zlib1g-dev \
        libopenjp2-7 \
	libatlas-base-dev
COPY build/requirements.txt /opt/build/requirements.txt
RUN python3 -m pip install \
    --extra-index-url https://www.piwheels.org/simple \
    --requirement /opt/build/requirements.txt

# Apache / WSGI の設定
COPY build/etc/apache2/sites-available/* /etc/apache2/sites-available/
COPY build/etc/apache2/mods-available/* /etc/apache2/mods-available/
COPY build/etc/apache2/conf-available/* /etc/apache2/conf-available/
COPY build/etc/apache2/apache2.conf /etc/apache2/apache2.conf
COPY build/etc/apache2/envvars /etc/apache2/

# 診断AIデーモンの実行権限設定
RUN adduser --disabled-password --gecos "" diagnose-ai
RUN groupadd ai-and-server
RUN usermod --append --groups ai-and-server diagnose-ai
RUN usermod --append --groups ai-and-server www-data
RUN mkdir --parents --mode=770 \
    /var/www/maff_ai/htdocs/tmpImage \
    /var/www/maff_ai/htdocs/resultImage
RUN chgrp ai-and-server \
    /var/www/maff_ai/htdocs/tmpImage \
    /var/www/maff_ai/htdocs/resultImage

# ソースのコピーとディレクトリ作成
COPY src /var/www/maff_ai/src
RUN mkdir --mode=700 /var/www/maff_ai/log
RUN chown www-data /var/www/maff_ai/log

# python3 -u: Disable Python buffer
# https://www.reddit.com/r/docker/comments/gk262t/comment/fqos8j8
CMD ["bash", "/var/www/maff_ai/src/main.sh"]

