from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json

load_dotenv()

_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

_SUMMARIZE_SYSTEM = """You are a SQL query result analyzer and summarizer.
You will receive a SQL query and its result rows.
If asked for tables then only provide the tables else just provide the required output
"""


def _truncate_result(query_result: list, max_rows: int = 20) -> str:
    """Truncate large result sets to avoid token overflow."""
    total = len(query_result)
    if total == 0:
        return "No rows returned."
    if total <= max_rows:
        return json.dumps(query_result, default=str)
    
    sample = query_result[:max_rows]
    return (
        f"Total rows: {total}. Showing first {max_rows}:\n"
        + json.dumps(sample, default=str)
    )


def summarization_node(state: dict) -> dict:
    """Summarizes query_result into a human-friendly message.
    Single direct LLM call — no agent, no loop."""
    sql_query    = state.get("sql_query", "")
    query_result = state.get("query_result", [])  # ← correct key

    truncated = _truncate_result(query_result)

    response = _llm.invoke([
        SystemMessage(content=_SUMMARIZE_SYSTEM),
        HumanMessage(content=(
            f"SQL Query:\n{sql_query}\n\n"
            f"SQL Result:\n{truncated}"
        )),
    ])

    print(f"[SUMMARIZE] → done ({len(query_result)} row(s))")
    return {"messages": [AIMessage(content=response.content)]}