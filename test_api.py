import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_api():
    """Test if the OpenAI API key is working correctly by making a simple API call."""
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
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Make a simple test query
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message. Please respond with 'API connection successful'."}
            ],
            max_tokens=20
        )
        
        # Check if response was successful
        if response and response.choices and len(response.choices) > 0:
            print(f"✅ API connection successful!")
            print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ Error: Received empty response from API")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    success = test_openai_api()
    if not success:
        sys.exit(1)  # Exit with error code
    print("Test completed successfully") 