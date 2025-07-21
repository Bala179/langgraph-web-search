from dotenv import load_dotenv
from typing import Annotated, Sequence
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition

# Load API Keys
load_dotenv()

# Load FastAPI
app = FastAPI()

# Request model
class SearchRequest(BaseModel):
    search_input: str

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
    """Invoke the LLM with the user input."""
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

app.conversation_history = []
MAX_HISTORY_LENGTH = 20

@app.get("/")
def read_root():
    """Sample endpoint to test if the server is running."""
    return {"message": "Hello, WebSearchAgent is live!"}

# Conversation with AI agent
@app.post("/web_search")
async def web_search(request: SearchRequest):
    """Using OpenAI, generate an answer to the user's query using Tavily if necessary."""

    app.conversation_history.append(HumanMessage(content=request.search_input))
    if len(app.conversation_history) > MAX_HISTORY_LENGTH:
        app.conversation_history = app.conversation_history[-MAX_HISTORY_LENGTH:]

    result = graph.invoke({"messages": app.conversation_history})
    
    app.conversation_history = result['messages']
    if len(app.conversation_history) > MAX_HISTORY_LENGTH:
        app.conversation_history = app.conversation_history[-MAX_HISTORY_LENGTH:]

    return result['messages'][-1]