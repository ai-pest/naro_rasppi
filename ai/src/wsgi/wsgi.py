# -*- encoding: UTF-8 -*-
## wsgi.py 
## サーバ側インターフェース
'''
20200910: ひらがなとカタカナの作物名変換を追加、全体的な構造修正
20201112: リクエストと異なるIDをレスポンスとして返すバグがあったため修正
20210325 [v3] APIv4対応: 部位と果実によるフィルタリングを実装
20210510 [v4] APIv4対応
    識別サーバに部位を渡すように処理を修正
    B-Box を可視化して返す機能を追加（V4のみ）
    複数の葉・果実を検知した場合は、それぞれの物体の推論結果とGrad-CAMを返す機能を追加
20210702 [v4.1] 
    APIサーバのWebページ以外からリクエストを受けた場合、画像を返さないように変更
20210825 [v4.2] 
    リクエストデータをログに出力する処理を追加
20220204 [v5]
    APIv5対応
'''

import base64
import copy
import json
import logging.config
from pathlib import Path
import random
import time

# ログ設定ファイルからログ設定を読み込む
root_dir = Path(__file__).parent
logging.config.fileConfig(root_dir/"logging.conf")

INPUT_IMAGE_DIR = Path("/var/www/maff_ai/htdocs/tmpImage/")
OUTPUT_IMAGE_DIR = Path("/var/www/maff_ai/htdocs/resultImage/")


def remove_image_from_asset(assets):
    '''アセットから画像を削除する
    引数
        asset [dict] アセット
    返り値
        [dict] アセットから画像を削除したもの
    '''
    assets_without_image = copy.deepcopy(assets)

    for asset in assets_without_image["assets"]:
        for image in asset["images"]:
            del image["data"]

    return assets_without_image


def is_jpg(byte):
    return byte[:2] == b'\xff\xd8'


## TODO: 値の検査処理をまとめる
def get_plant(asset):
    '''アセットから作物名を取り出して返します
    作物名がひらがなの場合はカタカナに変換して返します
    引数
        asset [dict] アセット
    返り値
        plant [ustr] 作物名（カタカナに変換済み） 
    '''
    plant = asset["attributes"]["plant"]    # ustr
    hira2kata = {u'いちご': u'イチゴ', u'きゅうり': u'キュウリ', u'なす': u'ナス'}
    if plant in hira2kata.keys(): 
        plant = hira2kata[plant]

    if plant not in (u'トマト', u'イチゴ', u'キュウリ', u'ナス'):
        raise ValueError('Unsupported plant {} is selected.'.format(plant.encode('utf-8')))

    return plant


def get_part(asset):
    '''アセットから部位名を取り出して返します
    部位名が "葉"、"果実"、"花" 以外のときや、部位名がないときは
    "葉" を返します

    引数
        asset [dict] アセット
    返り値
        part [ustr] 部位名
    '''
    try:
        part = asset["attributes"]["part"]
        if part in ("葉", "果実", "花"):
            return part
    except KeyError:
        pass

    return '葉'


def get_category(asset):
    '''アセットから病害虫の種別を取り出して返します
    引数
        asset [dict] アセット
    返り値
        str 病害虫の種別（"病害"、"虫害" または ""=未指定）
    '''
    try:
        category = asset["attributes"]["category"]
        if category in ("病害", "虫害"):
            return category
    except KeyError:
        pass

    return ""


def issue_query(image_b, plant, part):
    '''クエリを発行します
    引数
        image_b [str?] 画像バイナリ
        plant [str] 作物名 空は不可
        part [str] 部位 空は不可
    返り値
        random_name [str] クエリと推論デーモンの応答ファイルを紐づけるトークン（内部管理用）
    '''

    random_name = "".join(
        [random.choice("1234567890abcdefghijklmnopqrstuvwxyz") for x in 
         range(10)])

    input_image_path = INPUT_IMAGE_DIR / f"{random_name}.jpg"
    input_json_path = INPUT_IMAGE_DIR / f"{random_name}.json"

    with open(input_image_path, 'wb') as fi, open(input_json_path, 'w') as fj:
        fi.write(image_b)
        request_data = {
            'plant': plant, 
            'part': part, 
        }
        json.dump(request_data, fj)

    return random_name


def remove_unmatched_category(results, category):
    """識別AIの検出結果から、ユーザ指定の病害虫種別と一致しない結果を削除する
    種別が「健全」のクラスは、フィルタせず返す

    Params:
        results: list 識別AIから書き出された診断結果 (JSON)
        category: カテゴリ名（"虫害"、"病害"、""=指定なし、のいずれか）
    """
    if category == "":
        return results

    filter_fn = lambda cls: cls["病害虫の種別"] in (category, "健全")

    return list(filter(filter_fn, results))


def remove_unmatched_plant(results, plant):
    """識別AIの検出結果から、ユーザ指定の作物名と一致しない結果を削除する
    """
    filter_fn = lambda cls: (cls["作物"] == plant)
    return list(filter(filter_fn, results))


def remove_unmatched_part(results, part):
    """識別AIの検出結果から、ユーザ指定の部位名と一致しない結果を削除する
    """
    filter_fn = lambda cls: (cls["部位"] == part)
    return list(filter(filter_fn, results))


def await_response(random_name):
    """与えられたトークンに対する推論デーモンのレスポンスを待ち、
    レスポンスを返す

    Args:
        random_name [str] クエリと検出結果を紐づけるトークン（内部管理用）
    Returns:
        dict, 推論デーモンのレスポンス
    """
    response_path = OUTPUT_IMAGE_DIR / f"{random_name}.json"

    while True:
        try:
            with response_path.open("r") as f:
                daemon_resp = json.load(f)
            response_path.unlink()
            return daemon_resp
        except (IOError, json.JSONDecodeError):
            time.sleep(0.01)


def bake_asset(
        asset_id, image_b, random_name, plant, part, category):
    '''指定されたクエリIDに対応するレスポンスの asset を作成します
    引数
        asset_id [str] APIのリクエストとレスポンスを紐づけるID
        image_b [binary] 元画像（JPEG）ファイル
        random_name [str] クエリと検出結果を紐づけるトークン（内部管理用）
        plant [ustr] 作物名
        part [ustr] 部位名
        category [ustr] 病虫害の種別
    返り値
        asset [dict] APIレスポンスの "assets" に入る辞書
    '''
    daemon_resp = await_response(random_name)

    daemon_results = daemon_resp['results']

    ## フィルタ
    daemon_results = remove_unmatched_category(daemon_results, category)
    daemon_results = remove_unmatched_plant(daemon_results, plant)
    daemon_results = remove_unmatched_part(daemon_results, part)

    ## レスポンスをフォーマット
    ## candidates: [list of dicts] 予測値
    ##   probability: 確信度（4桁丸め、0<=p<=1）
    ##   estimated: 予測クラス（作物名・部位名でフィルタ、害虫種別のみ表示）
    candidates = [
        {
            "probability": round(result["確信度"],4),
            "estimated": result["クラス名"],
            "pestId": "XX-XX-XX"
        } for result in daemon_results]

    # 上位5項目だけ返す（5項目未満のときは穴埋め）
    n = 5
    candidates = candidates[:n]
    if len(candidates) < n:
        candidates = candidates + \
                     [{'probability': 0.00, 'estimated': '', "pestId": "XX-XX-XX"}] * (n - len(candidates))

    asset = {
        "id": asset_id,
        "images" : [{
             "results": [{
                 "candidates": candidates,
             }],
        }],
    }

    return asset


def _application(environ, start_response):
    '''メイン関数
    '''
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    reqData = json.loads(request_body)
    logging.info(f'reqData: {remove_image_from_asset(reqData)}')

    status = '200 OK'
    response_header = [('Content-type','text/html')]
    start_response(status, response_header)

    ## リクエストの中身がなければエラーを返す
    if not ("assets" in reqData.keys()) or (len(reqData["assets"]) == 0):
        return [json.dumps({"status":"error", "type":"noFile"})]

    ## リクエストがある場合
    try:
        respAssets = []
        for reqAsset in reqData["assets"]:
            ## リクエストを解析
            filename = reqAsset["images"][0]["filename"]
            image_b = base64.b64decode(reqAsset["images"][0]["data"])
            plant = get_plant(reqAsset)
            part = get_part(reqAsset)
            category = get_category(reqAsset)

            ## FIXME: len(assets) >= 2 で、1枚だけ拡張子が.JPGでないときの動作を決める
            if (is_jpg(image_b) == False) or \
               (filename.split(".")[-1].lower() not in ("jpg", "jpeg")):
                return json.dumps({"status":"error", "type":"badExtension"});

            ## クエリを発行
            random_name = issue_query(image_b, plant, part)

            ## 結果をレスポンスの "asset" のフォーマットに整形
            respAsset = bake_asset(
                asset_id=reqAsset["id"], 
                image_b=image_b, 
                random_name=random_name, 
                plant=plant, 
                part=part,
                category=category,
            )
            respAssets.append(respAsset)

        ## レスポンスをまとめる
        response = {
            "assets": respAssets,
        }
        logging.info(f"Response: {response}")
        return json.dumps(response)

    except Exception as e:
        print(e)
        time.sleep(1)
        return json.dumps({
            "status": "error",
            "type": "Unknown",
        });


def application(environ, start_response):
    """Python3 対応 (PEP 3333)
    https://stackoverflow.com/a/52567975/13191651
    """
    res = _application(environ, start_response)

    ## Python3 では str が Bytestring ではなくなった
    ## bytestring に戻す
    if type(res) is list:
        return [bytes(res[0], encoding="utf-8")]
    else:
        res = bytes(res, encoding="utf-8")
        return [res]
