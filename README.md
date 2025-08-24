# LangGraph Web Search
A simple Tavily-powered chatbot application backend. To be used in conjunction with [this](https://github.com/Bala179/langgraph-web-search-frontend) repo.

## Steps for setup
1. Clone this repo.
2. Create a `.env` file in the base directory and insert the following content:
```
OPENAI_API_KEY=<your OpenAI API key>
TAVILY_API_KEY=<your Tavily API key>
```
3. Create an empty folder called `logs` in the base directory to store the logs.
4. Create a Python virtual environment named `venv`, activate it and use `pip install -r requirements.txt` to install the dependencies.
5. Follow the steps in the README of [this](https://github.com/Bala179/langgraph-web-search-frontend) repo to set up and start the frontend.
6. Run `uvicorn WebSearchAgent:app --reload` to start the backend.
7. Visit [http://localhost:4200/](http://localhost:4200/) and try chatting with the agent through the UI.

## Sample run of the application

https://github.com/user-attachments/assets/82164ed5-a33f-49e7-8e60-b926eee47d9b



## References
1. [https://docs.tavily.com/documentation/integrations/langchain](https://docs.tavily.com/documentation/integrations/langchain)
2. [https://dev.to/anuragkanojiya/how-to-use-langgraph-within-a-fastapi-backend-amm](https://dev.to/anuragkanojiya/how-to-use-langgraph-within-a-fastapi-backend-amm)
3. [https://www.youtube.com/watch?v=9L77QExPmI0](https://www.youtube.com/watch?v=9L77QExPmI0)
