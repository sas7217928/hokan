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
