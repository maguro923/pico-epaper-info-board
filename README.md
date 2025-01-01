# pico-epaper-info-board
Raspberry pi pico wとWaveshare Pico e-Paper 4.2、AHT20及びBME280を使用した情報掲示板です
## overview
現在時刻に加え、各種APIから取得した仮想通貨の価格及び株価、OpenWeatherAPIに基づく天気予報、センサーから取得した気温・湿度・気圧を表示します
左側面にあるボタンで表示を切り替えることができます
![25-01-01 21-16-38 1386](https://github.com/user-attachments/assets/d25758f9-6bab-498a-8c17-d93848c6a86c)
## How to use
この情報掲示板を作成するにあたって必要なものは以下の通りです

|商品名|備考|
|-----|-----|-----|
|Raspberry pi pico w|pico 2 wでの動作は未確認ですが、おそらく動作します|
|Waveshare Pico e-Paper 4.2|-|
|気圧・温度センサーモジュール BME280|BMP280での動作は未確認ですが、おそらく動作します|
|温度・湿度センサーモジュール AHT20|AHTx0やAHTx1での動作は未確認ですが、おそらく動作します|

この他各部品のはんだ付けや配線が必要なので、各自必要なものを用意してください

センサーモジュールはデフォルトのI2C通信に用いるピンに接続してください

ハードウェアの準備ができたら、example-private.pyをダウンロードしお手元の環境に合わせて値を入力してください
設定する値は以下を参考にしてください

|変数名|詳細|
|---|---|
|SSID|2.4Ghz帯が使用できるwifiのssid|
|PASSWORD|wifiのパスワード|
|OpenWeatherApiKey|OpenWeatherAPIのAPIキー|
|OpenWeatherCity|OpenWeatherAPIで取得する情報の地域(詳細はOpenWeatherApiのドキュメントを参照)|

値の入力が終わったらファイル名をprivate.pyに変更してください

最後にRaspberry pi pico wに以下のファイル・ディレクトリをコピーしてください
main.py
private.py
drivers

これで準備は完了です
Raspberry pi pico wの電源を入れると各種情報の取得が始まり電子ペーパーに描画されます

## In the end
元々は個人利用のために作成したプロジェクトですので、様々なバグや使い勝手の悪い点などあるかとと思います
このプログラムの改変は大歓迎です
是非別のサイズの電子ペーパーやほかのセンサーを搭載して自分好みにカスタマイズしてください
もし実際に試してみた方がいらっしゃいましたら、私のTwitter(X)に送っていただけると大変うれしいです
