# ブート用イメージの書き込み

ここでは、**可搬型識別装置のデータ（ブート用イメージ）を microSD カードに書き込む方法**を説明します。

作成した microSD カードを装着した Raspberry Pi は、病虫害識別装置として使うことができます。

> ⚠️注意⚠️
>
> ブート用イメージを書き込むと、**microSD カードにあるデータは削除されます**。
> 書き込み前に、カード内のデータを必ず確認してください。

## 用意するもの

* 書き込み作業用の Windows PC
* SDカードリーダ
* microSD カード（32GB以上）

## 書き込み手順

書き込み手順は下記のとおりです。

1. 書き込み用のアプリ（Raspberry Pi Imager）を、PCにインストールする
1. microSD カードを PC に接続する
1. ブート用イメージを microSD に書き込む

### 書き込み用のアプリを PC にインストールする

書き込み作業には、専用のアプリ（Raspberry Pi Imager）を使います。

1. Raspberry Pi の Web サイトにある、アプリの配布ページ (https://www.raspberrypi.com/software/) を開きます。  
1. 「Raspberry Pi Imager」をダウンロードします。  
![配布ページにある「Download for Windows」ボタンを押して、「Raspberry Pi Imager」をダウンロードする](./asset/burn_download.png)
1. ダウンロードしたファイルを開き、アプリをインストールします。  
![インストーラの「Install」ボタンを押して、アプリをインストールする](./asset/burn_installer.png)

### microSD カードを PC に接続する

PC に SD カードリーダを接続し、リーダに microSD カードを挿入します。

> ️📘ノート
>
> microSD の状態によっては、「microSD をフォーマットする必要がある」旨のメッセージが表示されることがありますが、無視してかまいません。
> 
> フォーマットは、書き込みアプリが自動的に実施します。
>
> ![「スキャンして修復しますか？」および「フォーマットする必要がある」旨のエラーメッセージ](./asset/burn_warning.png)

### ブート用イメージを microSD に書き込む

1. スタートメニューから書き込みアプリ「Raspberry Pi Imager」を選んで、アプリを起動します。  
![スタートメニューを開き、Raspyerrb Pi フォルダから Raspberry Pi Imager を選択する](./asset/burn_start_menu.png)
1. 書き込みアプリが起動します。  
![Raspberry Pi Imagerのメイン画面](./asset/burn_imager_main.png)
1. 「OSを選ぶ」ボタンを押し、一覧の最下部にある「カスタムイメージを使う」を選択します。  
![Raspberry Pi Imager で「OSを選ぶ」を選択](./asset/burn_imager_select_os.png)
![OSメニューから「カスタムイメージを使う」を選択](./asset/burn_imager_os_custom_image.png)
1. ブート用イメージを選択し、「Open」を押します。  
![ファイル選択画面で、ブート用イメージを選択](./asset/burn_imager_os_filepicker.png)
1. 「ストレージを選ぶ」ボタンを押し、書き込み対象の microSD カードを一覧から選択します。  
![Raspberry Pi Imager で「ストレージを選ぶ」を選択](./asset/burn_imager_select_storage.png)
![ストレージメニューから「SDXC Card」を選択](./asset/burn_imager_storage_sdxc.png)
1. 「書き込む」ボタンを押すと、microSD カードへの書き込みが始まります。
![Raspberry Pi Imager で「ストレージを選ぶ」を選択](./asset/burn_imager_write.png)
1. 書き込みが終了した旨のメッセージが表示されたら、microSD カードを PC から取り外します。
![「書き込みが正常に終了しました」というメッセージ](./asset/burn_imager_done.png)

Raspberry Pi に microSD カードを装着して起動すると、診断装置として使えるようになります。

装置をスマートフォンに接続して診断する方法は、「[診断装置の使い方](./how_to_use.md)」を参照してください。
