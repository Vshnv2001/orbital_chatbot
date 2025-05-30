from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from ai.LLMManager import LLMManager
from ai.guard import GuardAgent
from ai.ChatAgent import ChatAgent
from langchain_core.prompts import ChatPromptTemplate
from ai.State import State
from ai.PrunerAgent import PrunerAgent
from ai.SQLAgent import SQLAgent
from ai.SQLValidator import SQLValidator
from csv_processor import process_csv_files, get_engine
from ai.DatabaseManager import DatabaseManager
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a singleton instance of LLMManager
SYSTEM_PROMPT = "You are a helpful assistant that can answer questions about Orbital, a summer software engineering project course at the National University of Singapore. You are given a question and a file. You need to answer the question based on the file. If you don't know the answer, say 'I don't know'. Don't make up an answer."

def get_llm_manager():
    return LLMManager(system_prompt=SYSTEM_PROMPT)

class ChatMessage(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    # Process CSV files and generate metadata
    data_dir = os.path.join(os.path.dirname(__file__), "ai/kb/")
    if os.path.exists(data_dir):
        process_csv_files(data_dir)

@app.post("/chat")
async def chat(
    message: ChatMessage,
    llm_manager: LLMManager = Depends(get_llm_manager)
):
    state = State()
    state.question = message.message
    
    engine = get_engine()
    
    with engine.connect() as conn:
        # Fetch preprocessed table metadata
        result = conn.execute(text("SELECT * FROM table_metadata"))
        state.database_schema = result.fetchall()
        
        print("DATABASE SCHEMA:")
        print(state.database_schema)
        
        # Pass question to Pruner Agent to retrieve relevant tables and columns
        pruner_agent = PrunerAgent()
        state.is_relevant = pruner_agent.prune(state)
        
        print("IS RELEVANT:")
        print(state.is_relevant)
        
        if not state.is_relevant:
            return {"response": "I don't know. Please ask a question about your employees, projects, or departments."}
        
        db_uri = "postgresql://postgres:postgres@postgres:5432/postgres"
        
        db_manager = DatabaseManager(db_uri)
        sql_agent = SQLAgent(db_manager)
        state.sql_query = sql_agent.generate_sql(state)
        print("INITIAL SQL QUERY:")
        print(state.sql_query)
        
        sql_validator = SQLValidator()
        
        results = db_manager.execute_query(state,sql_validator)
        
        print("RESULTS:")
        print(results)
        
        chat_agent = ChatAgent()
        response = chat_agent.answer_question(results, state.question, state.sql_query)
        
    return {"response": response}