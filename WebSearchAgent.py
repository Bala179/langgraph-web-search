from dotenv import load_dotenv
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition

# Load API Keys
load_dotenv()

# Define state class
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Tavily search tool
search_tool = TavilySearch(max_results=2)
tools = [search_tool]

# OpenAI model with tools bound
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

# Chatbot node
def chatbot(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
        "You are my AI assistant, please answer my query to the best of your ability."
    )
    response = llm.invoke([system_prompt] + state["messages"]) 
    state['messages'] = AIMessage(content=response.content)

    print(f"\nAI: {response.content}")

    return state

# Build and compile graph
CHATBOT_NODE = "chatbot"
TOOL_NODE = "tools"

graph_builder = StateGraph(AgentState)
graph_builder.add_node(CHATBOT_NODE, chatbot)

tool_node = ToolNode(tools=[search_tool])
graph_builder.add_node(TOOL_NODE, tool_node)

graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)
graph_builder.add_edge(TOOL_NODE, CHATBOT_NODE)
graph_builder.add_edge(START, CHATBOT_NODE)
graph = graph_builder.compile()

# Conversation with AI agent
conversation_history = []
MAX_HISTORY_LENGTH = 20

while True:
    try:
        user_input = input("Type a message for the AI agent: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
    except:
        user_input = "What do you know about LangGraph?"
        print("Type a message for the AI agent: " + user_input)
        break

    conversation_history.append(HumanMessage(content=user_input))
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]

    result = graph.invoke({"messages": conversation_history})
    
    conversation_history = result['messages']
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]