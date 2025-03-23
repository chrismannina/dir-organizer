"""File indexer module for analyzing files with LLM."""

import json
import re
from typing import Dict, List

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from tqdm import tqdm

from llm_organizer.utils import format_naming_scheme


class FileIndexer:
    """Handles file indexing and LLM analysis using LlamaIndex."""

    def __init__(self, config: Dict):
        """
        Initialize the indexer with configuration.

        Args:
            config (Dict): Configuration dictionary containing API keys and model settings
        """
        self.config = config
        self.llm = OpenAI(api_key=config["openai_api_key"], model=config["model_name"])
        Settings.llm = self.llm
        Settings.chunk_size = 512
        Settings.chunk_overlap = 20

        # Set default naming schemes
        self.tags_naming_scheme = config.get("tags_naming_scheme", "snake_case")
        self.categories_naming_scheme = config.get(
            "categories_naming_scheme", "pascal_case"
        )
        self.folder_naming_scheme = config.get("naming_scheme", "snake_case")

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
            print("✅ API connection successful!")
            print(f"Response: {response}")
            return True

        except Exception as e:
            print(f"❌ API connection failed: {str(e)}")
            return False

    def analyze_files(
        self, files_metadata: List[Dict], metadata_store=None, use_cached=True
    ) -> List[Dict]:
        """
        Analyze files using LLM to extract tags and suggested folders.

        Args:
            files_metadata (List[Dict]): List of file metadata dictionaries
            metadata_store: Optional MetadataStore instance to check for cached results
            use_cached: Whether to use cached analysis results

        Returns:
            List[Dict]: List of file metadata with analysis results added
        """
        # Test API connection before processing files
        print("\n🔍 Testing API connection before analysis...")
        if not self.test_api_connection():
            print(
                "❌ API connection test failed. Please check your API key and try again."
            )
            return [
                {
                    "path": metadata["path"],
                    "tags": ["unclassified"],
                    "suggested_folder": "other",
                    "description": "Could not analyze file due to API connection issues",
                }
                for metadata in files_metadata
            ]

        results = []
        files_to_analyze = []

        # Check for cached results if metadata_store is provided and use_cached is True
        if metadata_store and use_cached:
            for metadata in files_metadata:
                file_path = metadata["path"]
                if metadata_store.has_analysis(file_path):
                    # Use cached result
                    cached_analysis = metadata_store.get_file_analysis(file_path)
                    if cached_analysis:
                        results.append(cached_analysis)
                        continue

                # If no cached result, add to list of files to analyze
                files_to_analyze.append(metadata)
        else:
            # If not using cache, analyze all files
            files_to_analyze = files_metadata

        # Print stats on cache usage
        if metadata_store and use_cached:
            print(
                f"\n📊 Using {len(results)} cached results, analyzing {len(files_to_analyze)} new files"
            )

        # If no files need analysis, return the cached results
        if not files_to_analyze:
            return results

        for metadata in tqdm(files_to_analyze, desc="Analyzing files"):
            try:
                # Create document for indexing
                doc_text = self._prepare_document_text(metadata)
                document = Document(text=doc_text)

                # Create index for the documen
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

                # Parse and format tags according to naming scheme
                tags = self._parse_tags_response(str(tags_response))
                formatted_tags = [
                    format_naming_scheme(tag, self.tags_naming_scheme) for tag in tags
                ]

                # Format folder name according to naming scheme
                suggested_folder = format_naming_scheme(
                    str(folder_response).strip(), self.folder_naming_scheme
                )

                # Get category from metadata or use a default
                category = metadata.get("category", "Other")
                formatted_category = format_naming_scheme(
                    category, self.categories_naming_scheme
                )

                analysis = {
                    "path": metadata["path"],
                    "tags": formatted_tags,
                    "suggested_folder": suggested_folder,
                    "description": str(description_response).strip(),
                    "category": formatted_category,
                }

                results.append(analysis)

            except Exception as e:
                print(f"Error analyzing {metadata['path']}: {str(e)}")
                # Add a basic analysis result for failed files
                results.append(
                    {
                        "path": metadata["path"],
                        "tags": ["unclassified"],
                        "suggested_folder": "other",
                        "description": "Could not analyze file content",
                        "category": metadata.get("category", "Other"),
                    }
                )

        return results

    def _prepare_document_text(self, metadata: Dict) -> str:
        """Prepare text for document creation from metadata."""
        parts = [
            f"Filename: {metadata['name']}",
            f"File type: {metadata['extension']}",
            f"MIME type: {metadata['mime_type']}",
            f"Size: {metadata['size']} bytes",
            f"Created: {metadata['created']}",
            f"Modified: {metadata['modified']}",
        ]

        # Add category information
        parts.append(f"Category: {metadata.get('category', 'Other')}")

        # Add any additional metadata, especially for images
        if "additional_metadata" in metadata and metadata["additional_metadata"]:
            parts.append("\nAdditional Metadata:")
            image_metadata = metadata["additional_metadata"]

            # Add image dimensions if available
            if "ImageWidth" in image_metadata and "ImageHeight" in image_metadata:
                parts.append(
                    f"Image Dimensions: {image_metadata['ImageWidth']}x{image_metadata['ImageHeight']} pixels"
                )

            # Add image format
            if "ImageFormat" in image_metadata:
                parts.append(f"Image Format: {image_metadata['ImageFormat']}")

            # Add EXIF data that might be useful for organization
            if "DateTimeOriginal" in image_metadata:
                parts.append(f"Date Taken: {image_metadata['DateTimeOriginal']}")

            if "Make" in image_metadata and "Model" in image_metadata:
                parts.append(
                    f"Camera: {image_metadata['Make']} {image_metadata['Model']}"
                )

            if "ImageDescription" in image_metadata:
                parts.append(f"Image Description: {image_metadata['ImageDescription']}")

            # Add location data if available
            if "GPSInfo" in image_metadata:
                parts.append("GPS Data: Available (location information)")

            # Include any other relevant metadata
            for key, value in image_metadata.items():
                if key not in [
                    "ImageWidth",
                    "ImageHeight",
                    "ImageFormat",
                    "DateTimeOriginal",
                    "Make",
                    "Model",
                    "ImageDescription",
                    "GPSInfo",
                    "ImageMode",
                ] and isinstance(value, (str, int, float)):
                    parts.append(f"{key}: {value}")

        if metadata["content"]:
            parts.append("\nContent preview:")
            # Limit content to avoid token limits
            parts.append(metadata["content"][:2000])

        return "\n".join(parts)

    def _parse_tags_response(self, response: str) -> List[str]:
        """Parse LLM response to extract tags."""
        try:
            # Try to extract JSON array from the response
            json_match = re.search(r"\[(.*?)\]", response.replace("\n", ""))
            if json_match:
                try:
                    # Try to parse the extracted JSON
                    tags_list = json.loads(f"[{json_match.group(1)}]")
                    if isinstance(tags_list, list):
                        # Filter out non-string items and cleanup
                        return [
                            str(tag).strip()
                            for tag in tags_list
                            if isinstance(tag, str)
                        ]
                except json.JSONDecodeError:
                    pass

            # If can't extract JSON, use a simpler approach
            if "," in response:
                # Split by commas
                tags = [tag.strip().strip("\"'[]") for tag in response.split(",")]
                return [tag for tag in tags if tag]
            else:
                # Split by spaces if no commas (less reliable)
                words = response.strip("[]\"' ").split()
                return [
                    word for word in words if len(word) > 2
                ]  # Filter out short words

        except Exception:
            pass

        # Fallback to unclassified
        return ["unclassified"]
