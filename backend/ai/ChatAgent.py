from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

class ChatAgent:
    def __init__(self):
        """Initialize the ChatAgent with OpenAI model."""
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create a system prompt template
        self.system_prompt = """You are a helpful AI assistant that answers questions based on SQL query results.
        The SQL results will be provided to you, and assume that the results are sufficient to answer the question.
        Always be concise and direct in your answers.
        Format numbers and dates appropriately.
        
        Only answer the user's question. Don't mention that you used a SQL query to answer the question.
        """

    def _format_sql_results(self, sql_results: List[Dict[str, Any]]) -> str:
        """Format SQL results into a readable string."""
        if not sql_results:
            return "No results found."
            
        # Get column names from the first row
        columns = list(sql_results[0].keys())
        
        # Create header
        formatted_output = "SQL Results:\n"
        formatted_output += " | ".join(columns) + "\n"
        formatted_output += "-" * (sum(len(col) for col in columns) + 3 * (len(columns) - 1)) + "\n"
        
        # Add rows
        for row in sql_results:
            formatted_output += " | ".join(str(row[col]) for col in columns) + "\n"
            
        return formatted_output

    def answer_question(self, sql_results: List[Dict[str, Any]], user_question: str, sql_query: str) -> str:
        """
        Answer a user's question based on the provided SQL results.
        
        Args:
            sql_results: List of dictionaries containing the SQL query results
            user_question: The user's question about the data
            
        Returns:
            str: The answer to the user's question
        """
        # # Format SQL results
        # formatted_results = self._format_sql_results(sql_results)
        
        # Create messages for the chat
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Here are the SQL results:\n{sql_results}\n\nUser question: {user_question}, SQL Query: {sql_query}")
        ]
        
        # Get response from the model
        response = self.llm.invoke(messages)
        
        return response.content
