import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent # Modern agent constructor
import mysql.connector

# Load environment variables (Make sure GROQ_API_KEY and GOOGLE_API_KEY are in your .env)
load_dotenv()

# Moved password to .env for security: os.getenv("DB_PASSWORD")
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "archit", # Consider changing to: os.getenv("DB_PASSWORD", "archit")
    "database": "porches",
    "dictionary": True
}

@tool
def get_db_schema():
    """Fetches the schema structure of a connected mysql database
       Returns all table names and their column creation layouts.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        if not tables:
            cursor.close()
            connection.close()
            return "The database is currently empty (has no tables)."
        
        schema_info = "MySQL Database Schema Structure: \n"

        for table_dict in tables:
            # Safely extract table name
            table_name = list(table_dict.values())[0]
            schema_info += f"\nTable: {table_name}\n"
            
            desc_cursor = connection.cursor(dictionary=True)
            desc_cursor.execute(f"DESCRIBE {table_name};")
            columns = desc_cursor.fetchall()
            
            for col in columns:
                schema_info += f" - {col['Field']}  ({col['Type']}) \n"
            desc_cursor.close()
            
        cursor.close()
        connection.close()
        return schema_info
    except Exception as e:
        return f"Error while retrieving MySQL schema : {str(e)}"

@tool 
def execute_query(sql_query: str):
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
        # Dictionary cursor is used by default because of db_config
        cursor = connection.cursor(dictionary=True) 
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            cursor.close()
            connection.close()
            return "Query executed but returned no rows."
        
        result_str = f"Total records Found : {len(rows)}\n"
        
        # FIXED: Added parentheses to keys()
        column_names = list(rows[0].keys())
        result_str += f"Columns : {', '.join(column_names)}\n"
        
        for row in rows:
            result_str += f"{str(list(row.values()))}\n"
            
        cursor.close()
        connection.close()
        return result_str
    except Exception as e:
        return f"MySQL query execution failed : {str(e)}"

tools = [get_db_schema, execute_query]

# Define System Prompt
system_prompt = """
You are a SQL query agent. You first fetch the schema of the database to understand its structure, 
and then you write and execute the SQL query to answer the user's question.
Only execute queries starting with "SELECT" for table data protection.
"""

# Agent 1: Gemini 
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
sql_db_agent = create_agent(
    model=llm_gemini,
    tools=tools,
    system_prompt =system_prompt
)

# Agent 2: Groq (FIXED: using a valid Groq model)
llm_groq = ChatGroq(model="openai/gpt-oss-120b") 
sql_chat_groq = create_agent(
    model=llm_groq,
    tools=tools,
    system_prompt=system_prompt
)

# Test the Groq Agent
print("Invoking Agent...\n")
response = sql_chat_groq.invoke({"messages": [("user", "Get the names of first 10 students with cgpa > 8.0")]}, debug = True)

# The final response is the content of the last message in the state
print(response)