from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.errors import GraphRecursionError

from dotenv import load_dotenv
load_dotenv()

tool = TavilySearch(
    max_results = 5,
    search_depth = "basic"
)

llm = ChatGroq(model = "llama-3.3-70b-versatile")
llm_g = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash')

tavily_search_agent_gemini = create_agent(
    model = llm_g,
    tools = [tool],
    system_prompt="""
        You are a agent which will fetch current information using the tavily search tool
        Return information of document with date of it's release.
        Strictly restrict to just india sites only for any shopping recommendations and give price of it in inr along with the shopping link.
        """
)


tavily_search_agent = create_agent(
    model = llm,
    tools = [tool],
    system_prompt="""
        You are a agent which will fetch current information using the tavily search tool
        Return information of document with date of it's release
        Strictly restrict to just india sites only for any shopping recommendations and give price of it in inr along with the shopping link.
        """,
)


def tavily_search_node(state: dict) -> dict:
    user_request = state.get("user_request", "")
    config = {"recursion_limit": 6}  # ~3 tool calls max
    try:
        result = tavily_search_agent.invoke(
            {"messages": [{"role": "user", "content": user_request}]},
            config
        )
        return {"messages": [result["messages"][-1]]}
    except GraphRecursionError:
        return {"messages": [{"role": "assistant", "content": "Reached search limit."}]}


"""
config = {"configurable":{"thread_id":"1"}}
response = tavily_search_agent.invoke({"messages":[("user", "Suggest me 5 pendrives up to 128 gb with their link and their price.")]}, config)
print(response["messages"][-1].content)
"""