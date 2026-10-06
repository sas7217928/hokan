# hokan — 明日の天気を毎日12時に通知

毎日 12:00 (JST) に、明日の天気・気温・降水確率を取得して通知します。
天気データは [Open-Meteo](https://open-meteo.com/)（APIキー不要）、実行は GitHub Actions の cron です。

## セットアップ

リポジトリの **Settings → Secrets and variables → Actions** で設定します。

通知先（使うものだけ、Secrets に登録）:

| Secret | 内容 |
| --- | --- |
| `NTFY_TOPIC` | [ntfy](https://ntfy.sh/) のトピック名（スマホアプリで購読）。推測されにくい名前にすること |
| `DISCORD_WEBHOOK_URL` | Discord の Webhook URL |
| `SLACK_WEBHOOK_URL` | Slack の Incoming Webhook URL |

場所（Variables、省略時は東京）: `PLACE_NAME` / `LATITUDE` / `LONGITUDE`

## 動作確認

- Actions タブ → *Daily weather* → *Run workflow* で手動実行
- ローカル: `python3 weather_notify.py`（通知先未設定なら標準出力のみ）
- テスト: `python3 -m unittest discover -s tests`

## 注意

GitHub Actions の cron は混雑時に数分〜数十分遅れることがあります。

## 画面にポップアップを出す（PC常駐モード）

定刻になると、PCの画面に自動でポップアップが出ます。スマホ等への通知（上記）とは別で、併用できます。

```sh
python3 weather_notify.py --daemon            # 毎日 12:00（このPCのローカル時刻）
python3 weather_notify.py --daemon --at 12:30 # 時刻変更
python3 weather_notify.py --popup             # 今すぐ1回だけ表示して試す
```

- 表示は tkinter のダイアログ（最前面）。使えない環境では macOS の通知 / Linux の `notify-send` に切り替わります。
  Linux で tkinter が無い場合は `sudo apt install python3-tk`。
- 12時にスリープしていた場合は、復帰後に（その日まだなら）表示します。
- 環境変数 `PLACE_NAME` / `LATITUDE` / `LONGITUDE` で場所を変えられます。

### ログイン時に自動で起動する

- **Windows**: `Win+R` → `shell:startup` を開き、`pythonw C:\path\to\weather_notify.py --daemon` を実行するショートカットを置く
- **macOS**: システム設定 → 一般 → ログイン項目に、上記コマンドを実行するシェルスクリプト（`.command`）を追加
- **Linux**: `~/.config/autostart/weather.desktop` に `Exec=python3 /path/to/weather_notify.py --daemon` を書く
