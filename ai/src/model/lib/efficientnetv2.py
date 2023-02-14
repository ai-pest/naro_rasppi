#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import csv
import time

import numpy as np
from PIL import Image


model_type = 'tflite'
isize = 512
tflite_path = '/var/www/maff_ai/src/model/bin/20221210_1004_ev2hub_ep3/model_lite.tflite'
classes_path = '/var/www/maff_ai/src/model/bin/20221210_1004_ev2hub_ep3/classes.csv'

class EfficeintNetV2():
    """A TFLite model of EfficeintNetV2 that receives images and returns
    prediction results.
    """
    def __init__(self):
        #from pycoral.utils.edgetpu import make_interpreter
        if model_type == 'tflite':
            import tflite_runtime.interpreter as tflite
            self.interpreter = tflite.Interpreter(model_path=tflite_path)
        else:
            raise NotImplementedError(
                f"Model type {model_type} is not supported."
                f" Use `tflite` instead.")

        with open(classes_path, "r") as f:
            self.classes = list(csv.DictReader(f))


    def infer(self, image_path):
        """Runs inference on the given image.
        Params:
            image_path
        Returns:
            np.array of probs. Each element is within the range of [0, 1].
        """
        image_array = self._preprocess_image(image_path)
        probs = self._predict(image_array)
        probs = probs[0]
        probs = (probs + 128) / 255
            # Convert probs range: [-128, 127] (quantized models) -> [0, 1]
        return probs


    def _preprocess_image(self, image_path):
        """Internal function that takes an image path and returns a numpy array
        that is processed for prediction on EfficeintNetV2 models
        """
        # Web API 側が画像の保存を終えるまで、リトライする
        open_patiently = lambda fp: do_patiently(
            Image.open, 100, 0.1, IOError, fp)
        with open_patiently(image_path) as im:
            im = im.resize((isize, isize))
            image_array = np.array(im)

        # preprocess the image for EfficientNetV2 models
        image_array = image_array - 128.0
        image_array = image_array.astype(np.int8)

        return image_array[None, ...]


    def _predict(self, image_array):
        """Internal function that for inference
        Params:
            image_array: an numpy array of images
        Returns:
            `numpy.ndarray` of predicted results
        """
        self.interpreter.allocate_tensors()
        self.interpreter.set_tensor(
            self.interpreter.get_input_details()[0]['index'], image_array)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(
            self.interpreter.get_output_details()[0]['index'])


def do_patiently(func, n_retries, interval_sec, ignore_error, *args, **kwargs):
    """与えられた関数を最大 n 回リトライし、その間エラーは無視する

    Params:
        func: 実行する関数
        n_retries: リトライ回数
        interval_sec: リトライ間隔（秒）
        ignore_error: 無視するエラーの型
        *args, **kwargs: func に渡す引数
    Returns:
        関数 func の実行結果
    """
    for i in range(n_retries - 1):
        try:
            return func(*args, **kwargs)
        except ignore_error:
            time.sleep(interval_sec)
            continue

    return func(*args, **kwargs)

