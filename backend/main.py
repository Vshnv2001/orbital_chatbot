from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai.LLMManager import LLMManager
from langchain_core.prompts import ChatPromptTemplate

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

@app.post("/chat")
async def chat(
    message: ChatMessage,
    llm_manager: LLMManager = Depends(get_llm_manager)
):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "{message}")
    ])
    response = llm_manager.invoke(prompt, message=message.message)
    # print(response)
    return {"response": response[0]['text']}