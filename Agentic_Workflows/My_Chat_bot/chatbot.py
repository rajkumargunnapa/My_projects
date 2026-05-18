from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
import os, sqlite3, uuid
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv(override=True)

def get_groq_llm():
    return ChatOpenAI(
        model="openai/gpt-oss-20b",
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3, max_tokens=2000
    )

sqlite_conn = sqlite3.connect("bot_checkpoint.sqlite", check_same_thread=False)
memory = SqliteSaver(sqlite_conn)
llm = get_groq_llm()

class BasicChatState(TypedDict): 
    messages: Annotated[list, add_messages]

def chatbot(state: BasicChatState): 
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(BasicChatState)
graph.add_node("chatbot", chatbot)
graph.add_edge("chatbot", END)
graph.set_entry_point("chatbot")
app = graph.compile(checkpointer=memory)

def run_chat(user_input: str, thread_id: str) -> str:
    """Run one step of the chatbot and return AI response."""
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    return result["messages"][-1].content

def new_thread_id() -> str:
    """Generate a new unique thread_id."""
    return str(uuid.uuid4())
