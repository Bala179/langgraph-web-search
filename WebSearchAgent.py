from dotenv import load_dotenv
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

graph_builder = StateGraph(AgentState)

search_tool = TavilySearch(max_results=2)
tools = [search_tool]

llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

def chatbot(state: AgentState) -> AgentState:
    return {"messages": [llm.invoke(state["messages"]) ]}

CHATBOT_NODE = "chatbot"
TOOL_NODE = "tools"

graph_builder.add_node(CHATBOT_NODE, chatbot)

tool_node = ToolNode(tools=[search_tool])
graph_builder.add_node(TOOL_NODE, tool_node)

graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)
graph_builder.add_edge(TOOL_NODE, CHATBOT_NODE)
graph_builder.add_edge(START, CHATBOT_NODE)
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break