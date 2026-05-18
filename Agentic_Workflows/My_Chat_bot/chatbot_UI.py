import streamlit as st
from chatbot import run_chat, new_thread_id

st.set_page_config(page_title="Raj's CHATGPT", layout="wide")

# Initialize session state
if "threads" not in st.session_state:
    st.session_state["threads"] = {}  # {thread_id: messages}
if "current_thread" not in st.session_state:
    st.session_state["current_thread"] = None
if "active" not in st.session_state:
    st.session_state["active"] = True

# Sidebar
with st.sidebar:
    st.title("💬 Happy to CHAT")

    # New Chat button
    if st.button("➕ New Chat"):
        tid = new_thread_id()
        st.session_state["threads"][tid] = []
        st.session_state["current_thread"] = tid
        st.session_state["active"] = True

    st.subheader("Past Chats")
    # Show all threads
    for tid in st.session_state["threads"].keys():
        if st.button(f"Chat {tid[:8]}", key=tid):  # show first 8 chars
            st.session_state["current_thread"] = tid
            st.session_state["active"] = True

# Current thread
current_tid = st.session_state["current_thread"]

st.title("Chat Interface")

if current_tid:
    messages = st.session_state["threads"][current_tid]

    # Display past messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if st.session_state["active"]:
        if user_input := st.chat_input("Type your message..."):
            if user_input.lower().strip() in ["exit", "end"]:
                st.session_state["active"] = False
                messages.append({"role": "assistant", "content": "Chat ended. Start a new chat from the sidebar."})
                with st.chat_message("assistant"):
                    st.markdown("Chat ended. Start a new chat from the sidebar.")
            else:
                messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                ai_response = run_chat(user_input, current_tid)
                messages.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
    else:
        st.info("Chat is inactive. Click 'New Chat' in the sidebar to start again.")
else:
    st.info("No chat selected. Start a new one from the sidebar.")
