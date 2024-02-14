import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from question_answering.question_answering import generate_response as generate_rag_response
from question_answering.question_answering import reset_memory


GREETING = "Welcome to the SmartCat AI Assistant! How may I assist you today?"

# App title
st.set_page_config(page_title="SmartCat AI Assistant", page_icon="🐱", layout="wide")

# Replicate Credentials
with st.sidebar:
    st.title('SmartCat AI Assistant')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    reset_memory()
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def generate_response(prompt_input):
    chat_history = [message["content"] for message in st.session_state.messages][1:]
    return generate_rag_response(prompt_input, chat_history)

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)