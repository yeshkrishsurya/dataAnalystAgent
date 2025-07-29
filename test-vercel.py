#!/usr/bin/env python3
"""
Test script for Vercel deployment
"""

import requests
import json
import tempfile
import os

def test_vercel_deployment(base_url):
    """Test the Vercel deployment"""
    
    print(f"🧪 Testing Vercel deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: Simple API test
    print("\n3. Testing API endpoint with simple question...")
    test_question = "What is 2 + 2?"
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_question)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = requests.post(
                    f"{base_url}/api/",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                print("✅ API endpoint passed")
                result = response.json()
                print(f"   Response type: {type(result)}")
                print(f"   Response preview: {str(result)[:200]}...")
            else:
                print(f"❌ API endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    
    return True

def main():
    """Main function"""
    # You can change this URL to your actual Vercel deployment
    base_url = "https://your-vercel-app.vercel.app"
    
    # Check if URL is still the default
    if "your-vercel-app" in base_url:
        print("⚠️  Please update the base_url in this script with your actual Vercel URL")
        print("   Example: https://data-analyst-agent-abc123.vercel.app")
        return
    
    test_vercel_deployment(base_url)

if __name__ == "__main__":
    main() 