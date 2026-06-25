from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from agents.get_db_schema import get_db_schema_node
from agents.sql_query_generator import sql_query_gen_node
from agents.maths_agent import maths_node
from agents.tavily_search import tavily_search_node
from agents.run_query import run_query_node
from agents.get_weather import get_weather_node
from agents.query_summarize import summarization_node

load_dotenv()



class GraphState(TypedDict):
    user_request: str                                       # original user input
    route: str                                              # "db", "maths", "search", or "get_weather"
    schema: str                                             # filled by get_db_schema_node
    sql_query: str                                          # filled by sql_query_gen_node
    query_result: list                                      # filled by run_query_node
    messages: Annotated[list[BaseMessage], add_messages]    # filled by downstream nodes



_llm_router = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

_router_agent = create_agent(
    model=_llm_router,
    tools=[],
    system_prompt="""You are a request classifier.
Given a user request, classify it into exactly one of these four categories:

- "db"          : request is about fetching, querying, or retrieving data from a database or students table
- "maths"       : request is about mathematical calculations or operations (add, subtract, multiply, divide, exponents, logs, etc.)
- "search"      : request is about current events, news, real-time information, or anything needing a web search
- "get_weather" : request is about fetching current weather, temperature, or forecast for any city

Reply with ONLY the single word: db  OR  maths  OR  search  OR  get_weather
No explanation, no punctuation, nothing else.
""",
)


def router_node(state: dict) -> dict:
    """Classifies user_request into db, maths, search, or get_weather."""
    user_request = state.get("user_request", "")

    response = _router_agent.invoke({
        "messages": [{"role": "user", "content": user_request}]
    })

    raw = response["messages"][-1].content.strip().lower()
    print(f"[ROUTER RAW] → '{raw}'")

    if "weather" in raw:
        route = "get_weather"
    elif "math" in raw:
        route = "maths"
    elif "search" in raw:
        route = "search"
    else:
        route = "db"

    print(f"[ROUTER] → {route}")
    return {"route": route}


def _route_decision(state: dict) -> str:
    return state.get("route", "db")


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    # nodes
    graph.add_node("router",         router_node)
    graph.add_node("get_schema",     get_db_schema_node)
    graph.add_node("generate_sql",   sql_query_gen_node)
    graph.add_node("run_query",      run_query_node)
    graph.add_node("summarize_query", summarization_node)
    graph.add_node("maths",          maths_node)
    graph.add_node("search",         tavily_search_node)
    graph.add_node("get_weather",    get_weather_node)

    # entry point
    graph.set_entry_point("router")

    # conditional routing
    graph.add_conditional_edges(
        "router",
        _route_decision,
        {
            "db":          "get_schema",
            "maths":       "maths",
            "search":      "search",
            "get_weather": "get_weather",
        },
    )

    # DB path — sequential pipeline
    graph.add_edge("get_schema",     "generate_sql")
    graph.add_edge("generate_sql",   "run_query")
    graph.add_edge("run_query",      "summarize_query")
    graph.add_edge("summarize_query", END)

    # direct-to-END paths
    graph.add_edge("maths",       END)
    graph.add_edge("search",      END)
    graph.add_edge("get_weather", END)

    return graph


app = build_graph().compile()