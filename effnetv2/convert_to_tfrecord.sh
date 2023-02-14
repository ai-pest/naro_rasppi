#!/bin/bash
#-*- encoding: utf-8 -*-
# convert_to_tfrecord.sh EfficientNetV2 の学習・評価用データセットを TFRecord 形式に変換する
#
# 使い方: bash convert_to_tfrecord.sh /path/to/repo /path/to/dataset_root

set -e
REPO_DIR="$1"
DATASET_DIR="$2"


function check_directory_existence() {
    if [[ ! -d "$1" ]]; then
        echo "Directory not found: $1"
        echo "Usage: bash convert_to_tfrecord.sh /path/to/repo /path/to/dataset_root"
        exit 1
    fi
}

function calculate_num_shards() {
    # TFRecord の各ファイルが100MB程度になるようなファイル数を計算する
    #
    # 与えられたディレクトリについて、
    # 全ファイルの容量を合計し、
    # その容量を100MB で割った値を返す。

    echo $(( $(du -Lad0 "$1" | cut -f1) / 100000 + 1 ))
}


check_directory_existence "${REPO_DIR}"
check_directory_existence "${DATASET_DIR}"

NUM_SHARDS_TRAIN=$(calculate_num_shards "${DATASET_DIR}/train")
NUM_SHARDS_VALIDATION=$(calculate_num_shards "${DATASET_DIR}/validation")

docker run \
    --tty \
    --volume "${REPO_DIR}":/work/repo \
    --volume "${DATASET_DIR}":/work/dataset \
    --user "${UID}" \
    --rm \
    effnet python /work/repo/effnetv2/imagenet_to_gcs.py \
        --raw_data_dir /work/dataset \
        --local_scratch_dir /work/dataset/tfrecord \
        --train_shards "${NUM_SHARDS_TRAIN}" \
        --validation_shards "${NUM_SHARDS_VALIDATION}"

