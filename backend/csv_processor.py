import pandas as pd
from sqlalchemy import create_engine, text
import os
from typing import List, Dict
from ai.LLMManager import LLMManager
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict

def get_engine():
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    return create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}")

def get_column_descriptions(df: pd.DataFrame) -> Dict:
    """
    Generates descriptions for columns and the table using LangChain with structured output.
    Returns a dictionary containing column descriptions and table description.
    """

    
    # Define the output schema using Pydantic
    class ColumnMetadata(BaseModel):
        column_descriptions: Dict[str, str] = Field(
            description="Dictionary mapping column names to their descriptions"
        )
        table_description: str = Field(
            description="A concise description of the table's purpose and contents"
        )
    
    # Create the output parser
    parser = JsonOutputParser(pydantic_object=ColumnMetadata)
    
    # Get sample data
    sample_data = df.head(3).to_dict('records')
    col_names = df.columns.tolist()
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at describing database tables and columns.
        Given a sample of data, generate clear and concise descriptions.
        Each column description should be at most 10 words.
        The table description should be at most 2 sentences."""),
        ("user", """Given the following columns: {col_names}
        And this sample data:
        {sample_data}
        
        {format_instructions}""")
    ])

    llm_manager = LLMManager()
    
    # Get the response
    response = llm_manager.invoke(
        prompt,
        col_names=col_names,
        sample_data=sample_data,
        format_instructions=parser.get_format_instructions()
    )
    
    # Parse the response
    metadata = parser.parse(response[0]['text'])
    return {
        'column_descriptions': metadata['column_descriptions'],
        'table_description': metadata['table_description']
    }

def process_csv_files(csv_dir: str = "ai/kb"):
    engine = get_engine()
    
    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        table_name = os.path.splitext(csv_file)[0]
        print(table_name)
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"))
            table_exists = result.scalar()
        
        if not table_exists:
            # Read and upload CSV
            df = pd.read_csv(os.path.join(csv_dir, csv_file))
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            
            # Generate metadata using LLM
            metadata = get_column_descriptions(df)
            
            # Store metadata
            with engine.connect() as conn:
                conn.execute(
                    text("""
                    INSERT INTO table_metadata (table_name, column_names, column_descriptions, table_description)
                    VALUES (:table_name, :column_names, :column_descriptions, :table_description)
                    ON CONFLICT (table_name) DO UPDATE
                    SET column_names = :column_names,
                        column_descriptions = :column_descriptions,
                        table_description = :table_description
                    """),
                    {
                        "table_name": table_name,
                        "column_names": list(metadata['column_descriptions'].keys()),
                        "column_descriptions": [f"{col}: {desc}" for col, desc in metadata['column_descriptions'].items()],
                        "table_description": metadata['table_description']
                    }
                )
                conn.commit() 