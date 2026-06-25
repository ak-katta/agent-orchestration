import mysql.connector

def run_query_node(state: dict) -> dict:
    """Executes the generated SQL and returns results."""
    sql_query = state.get("sql_query", "")

    connection = mysql.connector.connect(
        host='localhost',
        user='archit',
        password='archit',
        database='base_cnpj'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql_query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    return {"query_result": result}

    
""""
if __name__ == "__main__":
    query = "SELECT * FROM students WHERE cgpa > 8;"
    result = run_query_node(query)
    print(result)
"""