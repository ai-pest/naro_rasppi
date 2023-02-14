# 可搬型病虫害識別装置

---

## 作業の手引き

* **スマートフォンから診断する**には...  
  * [診断装置の使い方](docs/how_to_use.md) をご参照ください。
* **ブート用イメージをSDカードに書き込む**には...  
  * [ブート用イメージの書き込み](docs/burn_bootable_image.md) をご参照ください。
* **ソースコードを、既存の Raspberry Pi 等のサーバに展開する**には...
  * [ソースコードの展開](docs/deploy_from_source.md) をご参照ください。
* **作物・部位・識別病虫害を変更した、新たな識別AIを作成する**には...  
  * [識別AIの学習](docs/train_diagnosis_ai.md) で示した手順に沿って、AIを作成しサーバを構築します。
* **変更したソースコードや識別AIを、ブート用イメージとして再配布する**には...  
  * [ブート用イメージの作成](docs/create_bootable_image.md) をご参照ください。

---

## ディレクトリ構成

* `ai`: 識別AIデーモンと Web API の Docker イメージ
* `webui`: 簡易 Web UI の Docker イメージ
* `webapp_xplat`: クロスプラットフォーム版アプリ（**OSS 化不可**）
* `effnetv2`: 識別AIの学習に用いるプログラム等

## 起動方法

Docker Engine を入れて下記を実行：

```console
$ docker compose up --build --detach
```

ビルド完了後

1. `<ホストIPアドレス>` にアクセスすると、簡易 Web UI が起動します。
1. `<ホストIPアドレス>:8080` にアクセスすると、クロスプラットフォーム版アプリが起動します。

なお、ブランチを切り替えて再実行するとき、`docker compose` が正しく動作しないことがあります。
この場合は、下記を実行：

```console
$ docker compose down
```

ホストを再起動した場合、コンテナも自動で再起動するように設定されています。これを無効化するときは、`docker compose down` を実行してください。

## クロスプラットフォーム版

クロスプラットフォーム版アプリはビルドに時間がかかるので、`docker compose up --build` コマンドでは再ビルドしないように設定しています。
クロスプラットフォーム版を再ビルドするときは、下記を実行：

```console
$ # 再ビルド
$ docker compose -f docker-compose-build-webui.yml up --build

$ # サーバ起動
$ docker compose up --build
```

