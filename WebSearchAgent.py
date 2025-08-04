"""
References: 
https://docs.tavily.com/documentation/integrations/langchain
https://dev.to/anuragkanojiya/how-to-use-langgraph-within-a-fastapi-backend-amm
https://www.youtube.com/watch?v=9L77QExPmI0
"""

import json
import logging
import pathlib
import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model

# Load API Keys
load_dotenv()

# FastAPI lifespan to configure logging
@asynccontextmanager
async def lifespan(app: FastAPI):
    config_file = pathlib.Path("logging_configs/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)
    yield

# Create logger object
logger = logging.getLogger('web-search-agent')

# Load FastAPI
app = FastAPI(lifespan=lifespan)

# Request model
class SearchRequest(BaseModel):
    search_input: str

# Tavily search tool
tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)

# OpenAI model
llm = init_chat_model(model="gpt-4o", model_provider="openai", temperature=0)

# Set up Prompt with 'agent_scratchpad'
today = datetime.datetime.today().strftime("%D")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a helpful reaserch assistant, you will be given a query and you will need to
    search the web for the most relevant information. The date today is {today}."""),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for tool calls
])

# Create an agent that can use tools
agent = create_openai_tools_agent(
    llm=llm,
    tools=[tavily_search_tool],
    prompt=prompt
)

# Create an Agent Executor to handle tool execution
agent_executor = AgentExecutor(agent=agent, tools=[tavily_search_tool], verbose=True)

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

    stream_list = list(agent_executor.stream({"messages": app.conversation_history}))
    for s in stream_list:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            logger.info('\n' + message)
        else:
            logger.info('\n' + message.pretty_repr())
        
    result = stream_list[-1]
    app.conversation_history = result['messages']
    if len(app.conversation_history) > MAX_HISTORY_LENGTH:
        app.conversation_history = app.conversation_history[-MAX_HISTORY_LENGTH:]

    return result['messages'][-1]