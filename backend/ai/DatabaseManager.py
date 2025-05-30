import psycopg2
import time
from typing import List, Any, Optional
from ai.SQLValidator import SQLValidator
from ai.State import State
from ai.SQLAgent import SQLAgent

class DatabaseManager:
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
            

    def execute_query(self, state: State, sql_validator: SQLValidator, num_tries:int = 0) -> List[Any]:
        """Execute SQL query on the remote database and return results."""
        try:
            conn = psycopg2.connect(self.db_uri)
            cursor = conn.cursor()
            print("state.sql_query", state.sql_query)
            cursor.execute(state.sql_query)
            results = cursor.fetchall()
            count = 0
            while len(results) == 0 and count < 2:
                error = "No Results found. Please modify the query to return results. Perhaps you can relax the filters?"
                validated_sql_query = sql_validator.validate_and_fix_sql(state, error)
                state.sql_query = validated_sql_query.get('corrected_query', state.sql_query)
                cursor.execute(state.sql_query)
                results = cursor.fetchall()
                count += 1
            print("results", results)
            return results
        except Exception as e:
            print("Error executing query: ", str(e))
            print("Number of tries: ", num_tries)
            if num_tries >= 2:
                raise Exception(f"We were unable to generate a valid SQL query. Please rephrase your question.")
            else:
                validated_sql_query = sql_validator.validate_and_fix_sql(state, str(e))
                print("Validated SQL Query: ", validated_sql_query)
                state.sql_query = validated_sql_query.get('sql_query', state.sql_query)
                return self.execute_query(state, sql_validator, num_tries + 1)