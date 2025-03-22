from typing import Dict, List
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from tqdm import tqdm
import os

class FileIndexer:
    """Handles file indexing and LLM analysis using LlamaIndex."""
    
    def __init__(self, config: Dict):
        """
        Initialize the indexer with configuration.
        
        Args:
            config (Dict): Configuration dictionary containing API keys and model settings
        """
        self.llm = OpenAI(api_key=config['openai_api_key'], model=config['model_name'])
        Settings.llm = self.llm
        Settings.chunk_size = 512
        Settings.chunk_overlap = 20
    
    def test_api_connection(self) -> bool:
        """
        Test the API connection to ensure it's working properly.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Create a simple test document
            doc_text = "This is a test document to verify API connectivity."
            document = Document(text=doc_text)
            
            # Create a simple index
            index = VectorStoreIndex.from_documents([document])
            
            # Try a simple query
            query_engine = index.as_query_engine()
            response = query_engine.query("What is this document about?")
            
            # If we get here, it worked
            print(f"✅ API connection successful!")
            print(f"Response: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to OpenAI API: {type(e).__name__}: {str(e)}")
            return False
            
    def analyze_files(self, files_metadata: List[Dict]) -> List[Dict]:
        """
        Analyze files using LlamaIndex and LLM.
        
        Args:
            files_metadata (List[Dict]): List of file metadata dictionaries
            
        Returns:
            List[Dict]: List of analysis results for each file
        """
        # Test API connection before processing files
        print("\n🔍 Testing API connection before analysis...")
        if not self.test_api_connection():
            print("❌ API connection test failed. Please check your API key and try again.")
            return [{
                'path': metadata['path'],
                'tags': ['unclassified'],
                'suggested_folder': 'other',
                'description': 'Could not analyze file due to API connection issues'
            } for metadata in files_metadata]
        
        results = []
        
        for metadata in tqdm(files_metadata, desc="Analyzing files"):
            try:
                # Create document for indexing
                doc_text = self._prepare_document_text(metadata)
                document = Document(text=doc_text)
                
                # Create index for the document
                index = VectorStoreIndex.from_documents([document])
                
                # Query the LLM for analysis
                query_engine = index.as_query_engine()
                
                # Get tags
                tags_response = query_engine.query(
                    "What are the most relevant tags or categories for this file? "
                    "Return only a JSON array of strings."
                )
                
                # Get folder suggestion
                folder_response = query_engine.query(
                    "Based on the file's content and metadata, suggest an appropriate folder "
                    "name for organizing this file. Return only a single string."
                )
                
                # Get description
                description_response = query_engine.query(
                    "Provide a brief (max 2 sentences) description of this file. "
                    "Return only the description text."
                )
                
                analysis = {
                    'path': metadata['path'],
                    'tags': self._parse_tags_response(str(tags_response)),
                    'suggested_folder': str(folder_response).strip(),
                    'description': str(description_response).strip()
                }
                
                results.append(analysis)
                
            except Exception as e:
                print(f"Error analyzing {metadata['path']}: {str(e)}")
                # Add a basic analysis result for failed files
                results.append({
                    'path': metadata['path'],
                    'tags': ['unclassified'],
                    'suggested_folder': 'other',
                    'description': 'Could not analyze file content'
                })
        
        return results
    
    def _prepare_document_text(self, metadata: Dict) -> str:
        """Prepare text for document creation from metadata."""
        parts = [
            f"Filename: {metadata['name']}",
            f"File type: {metadata['extension']}",
            f"MIME type: {metadata['mime_type']}",
            f"Size: {metadata['size']} bytes",
            f"Created: {metadata['created']}",
            f"Modified: {metadata['modified']}"
        ]
        
        if metadata['content']:
            parts.append("\nContent preview:")
            # Limit content to avoid token limits
            parts.append(metadata['content'][:2000])
        
        return "\n".join(parts)
    
    def _parse_tags_response(self, response: str) -> List[str]:
        """Parse the tags response from the LLM."""
        try:
            # Try to extract JSON array from response
            import json
            response = response.strip()
            if response.startswith("[") and response.endswith("]"):
                return json.loads(response)
            else:
                # Fall back to simple string splitting if JSON parsing fails
                return [tag.strip() for tag in response.split(",")]
        except:
            return ['unclassified'] 