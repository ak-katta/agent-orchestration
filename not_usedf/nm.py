from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# ── import existing nodes ──────────────────────────
from agents.get_db_schema import get_db_schema_node
from agents.sql_query_generator import sql_query_gen_node
from agents.maths_agent import maths_node
from agents.tavily_search import tavily_search_node
from agents.run_query import run_query_node
from agents.get_weather import get_weather_node
from agents.query_summarize import summarization_node

import mysql.connector

load_dotenv()


class GraphState(TypedDict):
    user_request: str                                       # original user input
    route: str                                              # "db", "maths" or "search" or "get_weather"
    schema: str                                             # filled by get_db_schema_node
    sql_query: str                                          # filled by sql_query_gen_node
    query_result: list                                      # filled by run_query_node
    messages: Annotated[list[BaseMessage], add_messages]    # filled by maths_node / tavily_search_node / get_weather_node / summarization_node


llm_router = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

router_agent = create_agent(
    model=llm_router,
    tools=[],
    system_prompt="""You are a request classifier.
Given a user request, classify it into exactly one of these three categories:

- "db"     : request is about fetching, querying, or retrieving data from a database or students table and summarize the data too
- "maths"  : request is about mathematical calculations or operations (add, subtract, multiply, divide, exponents etc.)
- "search" : request is about current events, news, real-time information, or anything that needs web search
- "get_weather" : request is about fetching current weather, temperature, or forecast of any city

Reply with ONLY the single word: db   OR   maths   OR   search  OR  get_weather
No explanation, no punctuation, nothing else.
"""
)

def router_node(state: dict) -> dict:
    """Classifies user_request into db, maths, search or get_weather."""
    user_request = state.get("user_request", "")

    response = router_agent.invoke({
        "messages": [{
            "role": "user",
            "content": user_request
        }]
    })

    route = response["messages"][-1].content.strip().lower()
    print(f"[ROUTER RAW OUTPUT] → '{route}'")

    # Safety fallback — normalize to exact expected values
    if "weather" in route:
        route = "get_weather"
    elif "math" in route:
        route = "maths"
    elif "search" in route:
        route = "search"
    else:
        route = "db"

    print(f"[ROUTER] → routing to: {route}")
    return {"route": route}


# ─────────────────────────────────────────────
# CONDITIONAL EDGE FUNCTION
# ─────────────────────────────────────────────
def route_decision(state: dict) -> str:
    return state.get("route", "db")



# ─────────────────────────────────────────────
# GRAPH WIRING
# ─────────────────────────────────────────────
graph = StateGraph(GraphState)

# add all nodes
graph.add_node("router",       router_node)
graph.add_node("get_schema",   get_db_schema_node)
graph.add_node("generate_sql", sql_query_gen_node)
graph.add_node("run_query",    run_query_node)
graph.add_node("summarize_query",  summarization_node)
graph.add_node("maths",        maths_node)
graph.add_node("search",       tavily_search_node)
graph.add_node("get_weather",  get_weather_node)

# entry point always hits router first
graph.set_entry_point("router")

# router decides which branch
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "db":     "get_schema",
        "maths":  "maths",
        "search": "search",
        "get_weather": "get_weather"
    }
)

# DB path — sequential
graph.add_edge("get_schema",   "generate_sql")
graph.add_edge("generate_sql", "run_query")
graph.add_edge("run_query",   "summarize_query")
graph.add_edge("get_weather",  END)

# Maths and Search paths — straight to END
graph.add_edge("maths",  END)
graph.add_edge("search", END)
graph.add_edge("summarize_query", END)

app = graph.compile()


# ─────────────────────────────────────────────
# TEST RUNS
# ─────────────────────────────────────────────
if __name__ == "__main__":
    """
    print("\n" + "="*50)
    print("TEST 1: DB query")
    print("="*50)
    result = app.invoke({
        "user_request": "Get all students with cgpa greater than 8"
    })
    print("SQL:", result["sql_query"])
    print("Results:", result["query_result"])
    """

    print("\n" + "="*50)
    print("TEST 2: Maths query")
    print("="*50)
    result = app.invoke({
        "user_request": "What is 25 multiplied by 4 then subtract 10 and calculate what is log(20) and e^2?"
    })
    print("Answer:", result["messages"][-1].content)

    print("\n" + "="*50)
    print("TEST 3: Search query")
    print("="*50)
    result = app.invoke({
        "user_request": "Suggest me 5 pendrives upto 128 gb along with their link and price in rupees ₹ "
    })
    print("Answer:", result["messages"][-1].content)

    print("\n" + "="*50)
    print("TEST 4: Weather query")
    print("="*50)
    result = app.invoke({
        "user_request": "What is weather in Jodhpur ?"
    })
    print("Answer:", result["messages"][-1].content)
