from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotSdkDeprecatedIn30
from googlesearch import search
import json
import os
import subprocess
import warnings

warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)

import groq_history
chat_history = []  # チャット履歴を追加
user_messages = []  # ユーザーIDの履歴を追加
group_members = []  # グループメンバーを管理するリスト

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
  
  # 発言者のデータを取得
  user_id = event.source.user_id
  if user_id not in group_members:
      group_members.append(user_id)  # ユーザーをリストに追加

  # チャット履歴に発言を追加
  chat_history.append(event.message.text)
  user_messages.append(user_id)

  # 過去10回のチャットが3人以下で行われているか確認
  recent_users = set(user_messages[-10:])  # 最新10回の発言者を取得
  if len(recent_users) <= 3:
      line_bot_api.push_message(event.source.user_id, TextSendMessage(text="他の皆さんは意見ありますか？"))
      # 他の人に話を振った後、履歴をリセット
      user_messages.clear()
      chat_history.clear()

  msg_result:str = groq_history.chat(event.message.text, chat_history)
  if msg_result.split()[0] == "TRAVEL":
    travel_destination = msg_result.split()[1]
    search_results = search(f"travel to {travel_destination}", num_results=5)
    travel_info = "旅行先の情報:\n"
    for result in search_results:
      travel_info += f"- {result}\n"
    line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text=travel_info)
    )
  elif msg_result != "ISNOTEXPLICIT":
    # 自動応答のメッセージを返す（受け取ったJSON形式のデータをそのまま表示する）
    line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text=groq_history.chat(event.message.text, chat_history))
      # TextSendMessage(text=json.dumps(event.message.__dict__)+json.dumps(event.source.__dict__))
    )

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
