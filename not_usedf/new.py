from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
import mysql.connector

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

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
tools = [get_schema]

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful database assistant. Use tools to fetch the schema if asked."
)

response = agent.invoke({"messages": [{"role": "user", "content": "What is the schema of the db?"}]})
print(response["messages"][-1].content)