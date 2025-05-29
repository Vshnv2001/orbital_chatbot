import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import dotenv
from ai.file_store import create_vector_store
from langchain_core.messages import SystemMessage
dotenv.load_dotenv()


class LLMManager:
    # Manages the interaction with the LLM
    def __init__(self, model="gpt-4o", system_prompt: str = None):
        api_key = os.getenv("OPENAI_API_KEY")
        self.vector_store_ids = [create_vector_store()]
        self.llm = ChatOpenAI(model=model, temperature=0, api_key=api_key).bind_tools(
            [
                {"type": "file_search", "vector_store_ids": self.vector_store_ids}
            ]
        )
        self.system_prompt = system_prompt

    def invoke(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        # Invokes the LLM
        messages = prompt.format_messages(**kwargs)
        
        # Add system message if provided
        if self.system_prompt:
            messages.insert(0, SystemMessage(content=self.system_prompt))
            
        response = self.llm.invoke(messages)
        return response.content