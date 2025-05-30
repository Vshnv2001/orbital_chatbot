from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .State import State
from .LLMManager import LLMManager


class SQLAgent:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.llm_manager = LLMManager()

    def generate_sql(self, state: State) -> dict:
        """Generate SQL query based on parsed question and unique nouns."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''

You are an AI assistant that generates SQL queries based on user questions, database schema, and unique nouns found in the relevant tables. Generate a valid SQL query to answer the user's question.

Please do not put `` around the column names. Also, check the column descriptions (in schema) and types and make sure that the syntax of the input types are correct. A faulty example is "SELECT * FROM users WHERE age > '25'".
Another faulty example is SELECT rider, stage, rank FROM results_individual WHERE rank IS NOT NULL AND rider IS NOT NULL AND stage IS NOT NULL AND rank != ''. The error is invalid input syntax for type integer: ""
             
DO NOT do empty string checks like != '' or != 'N/A' on numeric columns.
             
You may get foreign keys. In that case, design the query in such a way that it uses the foreign key to get the data from the related table.

When dealing with aggregations:
1. Consider what level of detail (granularity) is needed before aggregating
2. Group by all relevant dimensions first if counting distinct occurrences
3. Use common table expressions to break down complex aggregations into steps

You are allowed to use common table expressions or views if that simplifies the query.
Important: Whenever possible, sort the results by the x-axis.
             
THE RESULTS SHOULD ONLY BE IN THE FOLLOWING FORMAT, SO MAKE SURE TO ONLY GIVE TWO OR THREE COLUMNS:
[[x, y]]
or 

[[label, x, y]].

Postgres is case-sensitive. Please make sure to add double quotes around the column names, table names, and schema names.

If a question involves searching for a string, always use the lower() function to search for strings and always compare with lower case string values, like:
SELECT * from "company" WHERE lower("name") IN ('apple', 'google');
This is a STRICT requirement.
             

When responding to questions that involve preferered category of each group,
the response should clearly show the greatest preferences of each group.

This is a STRICT requirement.

For example, if the query is about showing preferred category among various groups, make sure to group the results accordingly to each group and display the most relevant cateogry for each group. 


Only after everything is done then apply limit 10

SKIP ALL ROWS WHERE ANY COLUMN IS NULL or "N/A" or "".
Just give the query string. Do not format it. Make sure to use the correct spellings of nouns as provided in the unique nouns list. All the table and column names should be enclosed in backticks.
'''),
            ("human", '''

===User question:
{question}

===Relevant tables and columns:
{pruned_tables_columns}

Return the SQL Query in the following format:
{{
    "sql_query": string
}}

Generate SQL query string only. Do not include any other text.
'''),
        ])
        
        print("PRUNED TABLES AND COLUMNS:")
        print(state.pruned_tables_columns)
        print("QUESTION:")
        print(state.question)

        response = self.llm_manager.invoke(
            prompt, question=state.question, pruned_tables_columns=state.pruned_tables_columns)
        print("RESPONSE:", response[0])
        response = response[0]["text"]
        output_parser = JsonOutputParser()
        response = output_parser.parse(response)['sql_query']
        print("SQL QUERY:", response)
        return response
        