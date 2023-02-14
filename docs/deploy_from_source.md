# ソースコードの展開

ここでは、既存の Raspberry Pi OS にソースコードを展開して、病虫害識別装置として使用できるようにする方法を説明します。

## 目次

1. Docker Engine のインストール
1. Docker イメージ等のクリーンアップ設定
1. ソースコードの展開
1. Wi-Fi ルータの設定

## Docker Engine のインストール

最新版の Docker Engine をインストールします ([参照](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script))。

```console
$ curl -fsSL https://get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh
```

デフォルトでは、`docker` コマンドを使うには root 権限が必要です。
ユーザを `docker` グループに追加して、権限昇格せずに `docker` コマンドを使用できるように設定します。

```console
# usermod -aG docker naro-rasppi
```

再起動して、変更を適用します。

```console
# systemctl reboot
```

## Docker イメージ等のクリーンアップ設定

電源プラグを抜いて可搬型識別装置を停止した場合、通常のシャットダウン時（`poweroff` 等のコマンドを使った場合）に実施される Docker の終了処理が行われず、不要なファイルが残ってしまう場合があります。

不要なファイルが蓄積するとストレージの空き容量が小さくなってしまうため、`cron` を利用して、Raspberry Pi の起動時にクリーンアップ処理を実施します。

1. 下記コマンドを実行して、`cron` ファイルを開きます。
    ```console
    $ crontab -e
    ```
1. `cron` ファイルに下記の行を追加します。
    ```
    @reboot /usr/bin/docker system prune --all --force
    ```

## ソースコードの展開

> ⚠️注意⚠️
> 
> ソースファイルの改行コードが `LF` 以外の場合、システムが正しく動作しない場合があります。
> 
> Linux 以外の OS (Windows など) では、`LF` 以外の改行コードに自動変換される場合がありますので、ご注意ください。

1. SCP 等を用いて、ソースコード (`naro_rasppi`) をサーバ上の任意の場所に展開します。
1. Docker コンテナの起動コマンドを実行し、識別 AI および Web サーバを起動します。
    ```console
    $ cd /path/to/naro_rasppi # ソースコードの展開先ディレクトリに移動
    $ docker compose up --build --detach
    ```
1. `curl` コマンドを使って、サーバが起動していることを確認します。
    ```console
    $ curl localhost
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
    <head>
      <meta charset="utf-8">
      <title>病虫害AI 簡易識別装置</title>
    ...
    ```

## Wi-Fi アクセスポイントの設定

Raspberry Pi を Wi-Fi アクセスポイントとして使用できるように設定します。

参照: https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point

1. 必要なソフトウェアのインストールと有効化を行います。
    * `hostapd` (Wi-Fi アクセスポイントの構成用ソフトウェア) 
    * `dnsmasq` (DNS キャッシュおよび DHCP サーバ)
    * `netfilter-persistent`, `iptables-persistent` (ファイアウォール)
    ```console
    # apt install hostapd
    # systemctl unmask hostapd
    # systemctl enable hostapd
    # apt install dnsmasq
    # DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
    ```
1. `hostapd` の設定を行います。
    > ⚠️注意⚠️
    >
    > * 日本の電波法では、2.4GHz 帯を除く無線 LAN 周波数の屋外利用が規制されています ([参照](https://www.tele.soumu.go.jp/j/sys/others/wlan_outdoor/))。
    >   動作モード（`hw_mode`）やチャネル（`channel`）などを変更して、装置を屋外で使用する場合は、各種法令を確認してください。
    > 
    >   なお、下記の設定 (2.4Ghz 帯を使用) は、日本国内での屋外利用ができるように構成しています。
    ```console
    # vi /etc/hostapd/hostapd.conf
    ```
    下記のとおり設定します。
    ```
    country_code=JP
    interface=wlan0
    ssid=XXXXXXXXXX
    hw_mode=g
    channel=7
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase=XXXXXXXXXX
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=TKIP
    rsn_pairwise=CCMP
    # IEEE 802.11n
    # https://raspberrypi.stackexchange.com/a/91345/150701
    # https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf
    ieee80211n=1
    ht_capab=[HT40-]
    ```
    無線 LAN の SSID は `ssid` で、パスワードは `wpa_passphrase` で、それぞれ設定します。
1. DHCP サーバの設定を行います。
    ```console
    # vi /etc/dhcpcd.conf
    ```
    下記の設定を、ファイルの末尾に追加します。
    ```
    # Wi-Fi configuration:
    interface wlan0
    static ip_address=192.168.10.1/24
    nohook wpa_supplicant
    ```
1. DNS および DHCP サーバの設定を行います。
    ```console
    # cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
    # vi /etc/dnsmasq.conf
    ```
    下記の設定を追加します。
    ```
    interface=wlan0 # Listening interface
    dhcp-range=192.168.10.10,192.168.10.255,255.255.255.0,24h
                    # Pool of IP addresses served via DHCP
    domain=wlan     # Local wireless DNS domain
    address=/ai.local/192.168.10.1
                    # Alias for this router
    ```
1. 誤設定によってユーザが電波関連法規に抵触しないよう、 Raspberry Pi の無線 LAN 機能はデフォルトで無効化されています。  
下記のコマンドで、無線 LAN 機能を有効化します。
    ```console
    # rfkill unblock wlan
    ```
1. Raspberry Pi を再起動し、設定を適用します。
    ```console
    # systemctl reboot
    ```

## 動作確認

上記の設定をして Raspberry Pi を再起動すると、可搬型識別装置として使用できるようになります。

スマートフォン等から装置に Wi-Fi 接続し、診断ができることをご確認ください。

装置の使い方は、[診断装置の使い方](./how_to_use.md) をご参照ください。

## LICENSE 

Copyright © 2012-2023 Raspberry Pi Ltd and is licensed under a Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA) licence

以上