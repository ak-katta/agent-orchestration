from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
import mysql.connector


@tool
def get_schema() -> str:
    """Returns the schema of the MySQL database."""
    connection = mysql.connector.connect(
        host='localhost',
        user='archit',
        password='archit',
        database='base_cnpj'
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
"""
llm = ChatGroq(
    model="openai/gpt-oss-120b"
    )


tools = [get_schema]

agent = create_agent(
    model = llm,
    tools= tools,
    system_prompt = "You are a assistant agent and your work is to fetch the schema of a table. You return directly without adding anything")  

response = agent.invoke({"input": "What is the schema of all tables?"})
print(response)
"""
def get_db_schema_node(state):
    schema = get_schema.invoke({})
    return {
        "schema": schema
    }