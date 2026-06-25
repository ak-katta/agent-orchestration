from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

SQL_SYSTEM_PROMPT = """You are an expert MySQL query generator.
You will be given a user request and a database schema.
Generate a valid MySQL query that fulfills the request.
Return ONLY the raw SQL query — no explanation, no markdown, no backticks, no comments.
The query must be directly executable with mysql.connector.
"""

query_gen_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=SQL_SYSTEM_PROMPT
)

DEFAULT_REQUEST = "fetch all records from the students table"


def sql_query_gen_node(state: dict) -> dict:
    """LangGraph node — generates SQL query from state.

    Reads:
        state["user_request"] — what the user wants (falls back to default)
        state["schema"]       — DB schema from get_db_schema_node

    Returns:
        state["sql_query"]    — raw SQL string ready for execution
    """
    user_request = state.get("user_request") or DEFAULT_REQUEST
    schema = state.get("schema", "")

    response = query_gen_agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                f"User request: {user_request}\n\n"
                f"Database Schema:\n{schema}\n\n"
                f"Generate the MySQL query."
            )
        }]
    })

    sql_query = response["messages"][-1].content.strip()

    return {"sql_query": sql_query}


"""
if __name__ == "__main__":
    test_state = {
        "schema": "{'students': [{'Field': 'id', 'Type': 'int'}, {'Field': 'name', 'Type': 'varchar(100)'}, {'Field': 'grade', 'Type': 'char(1)'}]}",
        "user_request": "Get all students with grade A"
    }

    result = sql_query_gen_node(test_state)
    print(result["sql_query"])
"""
