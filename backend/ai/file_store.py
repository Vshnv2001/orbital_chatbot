from openai import OpenAI
import os

import dotenv

dotenv.load_dotenv()

def create_vector_store(file_path: str = "ai/kb/orbital_brief_25.pdf"):
    '''
    Creates a vector store from a file and returns the vector store id.
    If the vector store already exists, it returns the vector store id.
    '''
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    
    # List all vector stores and check if one with this name exists
    vector_stores = client.vector_stores.list()
    for store in vector_stores.data:
        if store.name == file_path:
            return store.id
    
    # If no existing vector store found, create a new one
    vector_store = client.vector_stores.create(
        name=file_path,
    )

    # Upload the file to the vector store
    client.vector_stores.files.upload_and_poll(        
        vector_store_id=vector_store.id,
        file=open(file_path, "rb")
    )

    return vector_store.id



