#!/usr/bin/python3
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotSdkDeprecatedIn30
import json
import os
import subprocess
import warnings

import groq_chat

warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("MSG_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
  signature = request.headers["X-Line-Signature"]
  body = request.get_data(as_text=True)
  print("Request body: " + body)
  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    print("Invalid signature. Please check your channel token/secret.")
    abort(400)
  return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  if event.reply_token == "00000000000000000000000000000000":
    print("no reply")
    return
  # Macで受信したメッセージを読み上げる
  #subprocess.Popen(["say", event.message.text])
  # 自動応答のメッセージを返す（受け取ったJSON形式のデータをそのまま表示する）
  line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=groq_chat.chat(event.message.text))
  )

if __name__ == "__main__":
  app.run(host="localhost", port=8000)