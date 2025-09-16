#!/usr/bin/env python3
"""
Simple test script to verify Gemini API connection
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test basic Gemini API connection"""
    try:
        from google import genai
        
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY not found in environment variables")
            print("Please create a .env file with your Gemini API key:")
            print("GEMINI_API_KEY=your_api_key_here")
            return False
        
        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
        
        # New client reads GEMINI_API_KEY from environment
        client = genai.Client()
        
        print("Testing basic text generation...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'Hello, Gemini is working!'"
        )
        
        print(f"Gemini response: {response.text}")
        print("Gemini API connection successful!")
        return True
        
    except ImportError:
        print("Error: google-genai package not installed")
        print("Run: pip install google-genai")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API connection...")
    success = test_gemini_connection()
    
    if success:
        print("\n✅ All tests passed! Your Gemini setup is working.")
    else:
        print("\n❌ Tests failed. Please check the errors above.")
