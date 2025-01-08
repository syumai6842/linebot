import os
from groq import Groq

import subprocess

def chat(input_text, chat_history):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    system_prompt = {
        "role": "system",
        "content": open('./reference.txt', 'r').read()
    }
    # 最初のリクエスト時にsystem_promptを追加
    if not chat_history:
        chat_history.append(system_prompt)
    
    # ユーザプロンプトの追加
    user_prompt = {"role": "user", "content": input_text}
    chat_history.append(user_prompt)
    
    # 履歴の長さを制限（それ以上前の問い合わせ内容は忘れる）
    if len(chat_history) > 10:
        wasure = chat_history.pop(1)  # system_promptを保持しつつ古い履歴を削除
    
    # LLMに問い合わせる
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[system_prompt, user_prompt],
        max_tokens=8000,
        temperature=1.0
    )
    
    # LLMの反応を返す
    print(response.choices[0].message.content)
    return response.choices[0].message.content

if __name__ == "__main__":
    chat_history = []  # 履歴を保持するリスト
    while True:
        text = input(">>> ") # 入力を促す表示
        if text == "": # 何も入力されなければ終了
            break
        # チャットで問い合わせる
        response = chat(text, chat_history)
        print("-->", chat_history) # 問い合わせ内容を表示
        print(response) # レスポンスを表示
