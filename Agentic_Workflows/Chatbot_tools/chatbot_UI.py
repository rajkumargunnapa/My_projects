import streamlit as st
from tools_chatgpt import run_chat, new_thread_id
from datetime import datetime

st.set_page_config(page_title="Raj's CHATGPT", layout="wide")

# Initialize session state
if "threads" not in st.session_state:
    st.session_state["threads"] = {}  # {thread_id: {"messages": [], "title": str, "created_at": str}}
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
        created_at = datetime.now().strftime("%d %b, %I:%M %p")
        st.session_state["threads"][tid] = {
            "messages": [],
            "title": f"💬 New Chat ({created_at})",
            "created_at": created_at
        }
        st.session_state["current_thread"] = tid
        st.session_state["active"] = True

    st.subheader("Past Chats")
    # Show all threads with titles and timestamps
    for tid, data in st.session_state["threads"].items():
        label = f"{data['title']} — 🕒 {data['created_at']}"
        if st.button(label, key=tid):
            st.session_state["current_thread"] = tid
            st.session_state["active"] = True

# Current thread
current_tid = st.session_state["current_thread"]

st.title("Raj's Generative Pre-trained Transformer")

if current_tid:
    thread_data = st.session_state["threads"][current_tid]
    messages = thread_data["messages"]

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

                ai_message = run_chat(user_input, current_tid)

                # Store raw content for history (string or dict)
                messages.append({"role": "assistant", "content": str(ai_message.content)})

                with st.chat_message("assistant"):
                    # If tool returned structured data
                    if isinstance(ai_message.content, dict):
                        tool_output = ai_message.content

                        if "result" in tool_output:  # Calculator
                            st.success(
                                f"➗ Calculator Result: {tool_output['first_num']} {tool_output['operation']} {tool_output['second_num']} = {tool_output['result']}"
                            )
                            thread_data["title"] = "➗ Math Chat"

                        elif "Global Quote" in tool_output:  # Stock price
                            quote = tool_output["Global Quote"]
                            st.markdown("📈 **Stock Price Result**")
                            st.table({
                                "Symbol": [quote.get("01. symbol", "")],
                                "Price": [quote.get("05. price", "")],
                                "Change": [quote.get("09. change", "")],
                                "Change %": [quote.get("10. change percent", "")]
                            })
                            thread_data["title"] = f"📈 Stock Chat ({quote.get('01. symbol', '')})"

                        else:
                            st.markdown("🛠️ **Tool Output**")
                            st.json(tool_output)
                            thread_data["title"] = "🛠️ Tool Chat"

                    else:
                        # Normal text response
                        st.markdown(ai_message.content)
                        # If no title yet, set a generic one based on first user input
                        if thread_data["title"].startswith("💬 New Chat"):
                            if "hello" in user_input.lower():
                                thread_data["title"] = "💬 General Chat"
                            elif any(word in user_input.lower() for word in ["stock", "price", "market"]):
                                thread_data["title"] = "📈 Stock Chat"
                            elif any(word in user_input.lower() for word in ["add", "multiply", "divide", "subtract"]):
                                thread_data["title"] = "➗ Math Chat"
                            else:
                                thread_data["title"] = f"💬 Chat: {user_input[:15]}..."
    else:
        st.info("Chat is inactive. Click 'New Chat' in the sidebar to start again.")
else:
    st.info("No chat selected. Start a new one from the sidebar.")
