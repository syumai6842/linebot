#!/usr/bin/python3
import os
from groq import Groq

def chat(input_text):
  client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
  system_prompt = {
    "role": "system",
    "content": open('/Users/kanayanaokyou/Documents/c_program/line/reference.txt', 'r').read()
  }
  user_prompt = {
    "role": "user", "content": input_text
  }
  chat_history = [system_prompt, user_prompt]
  response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=chat_history,
    max_tokens=200,
    temperature=1.0
  )
  return response.choices[0].message.content;

if __name__ == "__main__":
  while True:
    text = input(">>> ")
    if text == "":
      break
    print(chat(text))