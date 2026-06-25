from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# ─────────────────────────────────────────────
# NODE 1 — get_db_schema_node (no LLM)
# ─────────────────────────────────────────────
@tool
def get_schema() -> str:
    """Returns the schema of the MySQL database."""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='archit',
        database='porches'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    schema = {}
    for table in tables:
        table_name = list(table.values())[0]
        desc_cursor = connection.cursor(dictionary=True)
        desc_cursor.execute(f"DESCRIBE {table_name};")
        schema[table_name] = desc_cursor.fetchall()
        desc_cursor.close()
    cursor.close()
    connection.close()
    return str(schema)

def get_db_schema_node(state: dict) -> dict:
    schema = get_schema.invoke({})
    return {"schema": schema}


# ─────────────────────────────────────────────
# NODE 2 — sql_query_gen_node (uses LLM)
# ─────────────────────────────────────────────
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

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

    # Safety strip backticks
    if sql_query.startswith("```"):
        sql_query = sql_query.split("```")[1]
        if sql_query.lower().startswith("sql"):
            sql_query = sql_query[3:]
        sql_query = sql_query.strip()

    return {"sql_query": sql_query}


# ─────────────────────────────────────────────
# COMBINED TEST RUN (no LangGraph graph yet)
# ─────────────────────────────────────────────
if __name__ == "__main__":

    # Initial state — only user_request, nothing else yet
    state = {
        "user_request": "get all students with cgpa > 8"
    }

    print("=" * 50)
    print("STEP 1: Fetching schema...")
    state = {**state, **get_db_schema_node(state)}
    print("Schema fetched:")
    print(state["schema"])

    print("=" * 50)
    print("STEP 2: Generating SQL query...")
    state = {**state, **sql_query_gen_node(state)}
    print("Generated SQL:")
    print(state["sql_query"])

    print("=" * 50)
    print("Final state keys:", list(state.keys()))