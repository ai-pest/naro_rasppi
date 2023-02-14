#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import traceback

from lib import efficientnetv2
from lib import queue

read_from = '/var/www/maff_ai/htdocs/tmpImage'
write_to = '/var/www/maff_ai/htdocs/resultImage'


class Daemon():
    def __init__(self):
        self.model = efficientnetv2.EfficeintNetV2()
        self.config = {
            'read_from': '/var/www/maff_ai/htdocs/tmpImage',
            'write_to': '/var/www/maff_ai/htdocs/resultImage'
        }


    def run(self):
        """Runs inference on each image in the `read_from` directory, and
        stores the results in the `write_to` directory.
        """
        request_queue = queue.create(request_dir=read_from, response_dir=write_to)

        for task in request_queue:
            try:
                probs = self.model.infer(task.jpeg_path)

                # クラスごとに、CSVから取得した情報と識別結果 (confidence) を
                # まとめて保持
                results = [
                    {**cls, "確信度": float(prob)} # JSON 化可能にする
                    for cls, prob in zip(self.model.classes, probs)]
                results_sorted = sorted(
                    results,
                    key=lambda result: result["確信度"],
                    reverse=True)

                # レスポンスを返す
                resp = {
                    'model_version': 'v1',
                    'results': results_sorted,
                }
                task.respond(response=resp)
                print(f"Inference is done for {task.jpeg_path}")

            except Exception as e:
                print("[ERROR]")
                traceback.print_exc()

                task.respond_with_error()

            finally:
                task.close()

if __name__ == '__main__':
    daemon = Daemon()
    print("The daemon is now accepting prediction requests.")
    daemon.run()

