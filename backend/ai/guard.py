from langchain_core.prompts import ChatPromptTemplate
from ai.LLMManager import LLMManager
from langchain_core.output_parsers import JsonOutputParser

GUARD_SYSTEM_PROMPT = """You are a guard agent that determines if a question is relevant to Orbital, a summer software engineering project course at the National University of Singapore.

A question is relevant if:
- It asks about Orbital program details, requirements, or procedures
- It asks about software engineering concepts related to the course
- It asks about project management aspects of Orbital
- It asks about NUS-specific information about Orbital

A question is irrelevant if:
- It asks about topics completely unrelated to software engineering or NUS
- Contains inappropriate or harmful content
- Is not a question at all

Always respond with the following JSON format:
{{
    "verdict": "relevant" or "irrelevant"
}}
"""

class GuardAgent:
    def __init__(self):
        self.llm_manager = LLMManager(system_prompt=GUARD_SYSTEM_PROMPT)
        self.parser = JsonOutputParser()

    def guard(self, message):
        prompt = ChatPromptTemplate.from_messages([
            ("system", GUARD_SYSTEM_PROMPT),
            ("user", message)
        ])
        print("Invoking guard")
        response = self.llm_manager.invoke(prompt)
        parsed_response = self.parser.parse(response[0]['text'])
        return parsed_response
