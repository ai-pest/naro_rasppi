## EfficientNet
##
## イメージのビルド
##   $ docker build -t effnet
## コンテナ構築
##   $ docker run -itdv /path/to/cloned/repo:/work --name effnet effnet bash
## 学習
##   $ docker exec -it effnet bash

FROM tensorflow/tensorflow:1.15.3-py3

RUN apt-get update && apt-get install --yes libtcmalloc-minimal4 curl

## Google Cloud SDK (gsutil)
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
        | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - \
    && apt-get update -y \
    && apt-get install google-cloud-sdk -y

## Tensorflow-related stuff
RUN pip install --upgrade pip
RUN pip install \
    tensorflow_addons tensorflow-estimator tensorflow_datasets pyyaml \
    tensorflow_hub cloud-tpu-client sklearn google-cloud-storage \
    pandas

CMD bash
