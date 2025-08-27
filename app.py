import streamlit as st
import os
import requests
import shelve
from dotenv import load_dotenv
load_dotenv()

st.title("Blue Spark Technologies Developed with ❤️")


USER_AVATAR = "👩"
BOT_AVATAR = "🤖"
API_KEY = os.getenv("KNCMAP_API_KEY")
MODEL_NAME = "mistralai/mistral-7b-instruct"


def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])


def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages


if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])


for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL_NAME,
        "messages": st.session_state.messages
    }

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=body
    )
    result = response.json()

    if "choices" in result and len(result["choices"]) > 0:
        # ✅ Safe: extract the assistant’s response
        answer = result["choices"][0]["message"]["content"]
    elif "error" in result:
        # ✅ Show API error message properly
        answer = f"❌ API Error: {result['error'].get('message', 'Unknown error')}"
    else:
        # ✅ Catch unexpected cases
        answer = "❌ Unexpected response format from API."

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    save_chat_history(st.session_state.messages)

except Exception as e:
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(f"❌ Python Error: {str(e)}")
