import os
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI

def test_llama_index():
    """Test if llama_index can correctly connect to OpenAI API."""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return False
    
    # Print abbreviated API key for verification
    print(f"Using API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Initialize OpenAI for llama_index
        print("Initializing OpenAI for llama_index...")
        llm = OpenAI(api_key=api_key, model="gpt-3.5-turbo")
        Settings.llm = llm
        
        # Create a simple document
        print("Creating test document...")
        doc_text = """
        This is a test document.
        It contains some simple text to test the LlamaIndex integration with OpenAI.
        The purpose is to verify API connectivity.
        """
        document = Document(text=doc_text)
        
        # Create index
        print("Creating index...")
        index = VectorStoreIndex.from_documents([document])
        
        # Query the index
        print("Querying index...")
        query_engine = index.as_query_engine()
        response = query_engine.query("What is the purpose of this document?")
        
        # Display response
        print(f"✅ llama_index query successful!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error using llama_index with OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing llama_index with OpenAI API connection...")
    test_llama_index() 