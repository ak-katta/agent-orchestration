from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_groq import ChatGroq
import mysql.connector

db_config = {
    "host":"localhost",
    "user":"root",
    "password":"archit",
    "database":"porches",
    "dictionary": True
}

@tool
def get_db_schema():
    """Fetches the schema structure of a connected mysql database
       Returns all table names and their column creation layouts.
    """

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        if not tables:
            cursor.close()
            connection.close()
            return "The database is currently empty (has no tables)."
        
        schema_info = "MySQL Database Schema Structure: \n"

        for table_dict in tables:
            table_name = list(table_dict.values())[0]
            schema_info += f"\nTable: {table_name}\n"
            desc_cursor = connection.cursor(dictionary = True)
            desc_cursor.execute(f"DESCRIBE {table_name};")
            columns = desc_cursor.fetchall()
            
            for col in columns:
                schema_info += f" - {col['Field']}  ({col['Type']}) \n"
            desc_cursor.close()
        cursor.close()
        connection.close()
        return schema_info
    except Exception as e:
        return f"Error while retrieveing MySQL schema : {str(e)}"


@tool 
def execute_query(sql_query : str):
    """
    Executes only read-only MySQL query and returns raw results.
    Only SELECT statements are permitted. 
    Do not use UPDATE, INSERT, DELETE or any DDL statements. 
    """
    query = sql_query.strip()
    if not query.lower().startswith('select'):
        return "For security reasons, only select queries are allowed."
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            cursor.close()
            connection.close()
            return "Query executed but returned no rows."
        result_str = f"Total records Found : {len(rows)}\n"
        column_names = list(rows[0].keys())
        result_str += f"Columns : {', '.join(column_names)}\n"
        for row in rows:
            result_str += f"{str(list(row.values()))}\n"
        cursor.close()
        connection.close()
        return result_str
    except Exception as e:
        return f"MySQL query execution failed : {str(e)} "
        
        

tools = [get_db_schema, execute_query]

llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")

sql_db_agent = create_agent(
    model = llm,
    tools = tools,
    system_prompt = """
    You are a SQL query agent. You fetch the schema of a database and then execute the query.
    Only execute query starting with "select" for table data protection.
    """
    )


sql_chat_groq = create_agent(
    model = ChatGroq(model = "openai/gpt-oss-120b"),
    tools = tools,
    system_prompt = """
    You are a SQL query agent. You fetch the schema of a database and then execute the query.
    Only execute query starting with "select" for table data protection.
    """
)

response = sql_chat_groq.invoke({"messages":[('user','Get the names of first 10 students with cgpa > 8.0')]})
print(response["messages"][-1].content)
