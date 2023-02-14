#!/usr/bin/env python3
#-*- encoding: utf-8 -*-
#
# ファイルベースのキューを用いた、Web API と診断AIのインターフェース
# （診断AI側）

import json
import time
from pathlib import Path


def create(request_dir, response_dir):
    """ファイルベースのキューを作成する。

    Params:
        request_dir: 診断リクエストデータ（画像とJSONメタデータ）が投入される
            ディレクトリ
        response_dir: 診断結果（JSON形式）の書き出し先ディレクトリ
    Yields:
        FileBasedTask キューに入った診断リクエスト
    """
    request_dir = Path(request_dir)
    response_dir = Path(response_dir)

    while True:
        time.sleep(0.01) # すこし待たないと、CPUを100%使ってしまう
        jpegs = _list_jpeg(request_dir)

        if len(jpegs) == 0:
            continue

        request_jpeg = jpegs[0]
        request_json = request_dir / f"{request_jpeg.stem}.json"
        response_json = response_dir / f"{request_jpeg.stem}.json"

        yield FileBasedTask(request_jpeg, request_json, response_json)


def _list_jpeg(dir_path):
    """指定されたディレクトリにあるJPEGファイルパスを返す

    Params:
        dir_path
    Returns:
        pathlib.Path の配列
    """
    paths = list(Path(dir_path).glob('*.*'))
    return [
        path for path in paths if path.suffix.lower() in ('.jpg', '.jpeg')]


class FileBasedTask():
    """キューに入った1個のタスク（診断リクエスト）を表すオブジェクト。

    リクエストの読み出し・レスポンスの書き込みを管理する。

    Params:
        jpeg_path: 診断リクエスト（JPEG画像）のファイルパス
        metadata_path: 診断リクエスト（JSON 形式メタデータ）のファイルパス
        response_path: 診断結果（JSON形式）の書き出し先ファイルパス
    """

    def __init__(self, jpeg_path, metadata_path, response_path):
        self.jpeg_path = jpeg_path
        self.metadata_path = metadata_path
        self.response_path = response_path


    def respond(self, response):
        """リクエストに対するレスポンスを返す

        Params:
            response: API サーバに返すレスポンス、JSON 化可能な形式
        """
        with open(self.response_path, mode='w') as f:
            json.dump(response, f)


    def respond_with_error(self):
        """リクエストに対して、エラーレスポンスを返す
        """
        error_resp = {
            'model_version': 'ERROR',
            'results': [
                {'bbox': [], 'pred_y': [], 'confidence': []},
            ],
        }
        with open(self.response_path, mode='w') as f:
            json.dump(error_resp, f)


    def close(self):
        """タスクを終了する
        """
        # リクエスト画像とメタデータを削除する
        self.jpeg_path.unlink()
        self.metadata_path.unlink()

