#!/usr/bin/env python3
"""
Test script to verify Vercel deployment will work
"""

import json
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ Matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ Matplotlib import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import beautifulsoup4
        print("✅ BeautifulSoup4 imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup4 import failed: {e}")
        return False
    
    return True

def test_agent_import():
    """Test that the agent can be imported"""
    print("\nTesting agent import...")
    
    try:
        from agent.data_analyst_agent import DataAnalystAgent
        print("✅ DataAnalystAgent imported successfully")
        return True
    except ImportError as e:
        print(f"❌ DataAnalystAgent import failed: {e}")
        return False

def test_tools():
    """Test that the tools work correctly"""
    print("\nTesting tools...")
    
    try:
        from agent.tools.data_tools import DataTools
        data_tools = DataTools()
        print("✅ DataTools initialized successfully")
        
        # Test data analysis
        test_data = [
            {"x": 1, "y": 2},
            {"x": 2, "y": 4},
            {"x": 3, "y": 6}
        ]
        
        analysis_input = json.dumps({
            "data": test_data,
            "analysis_type": "describe"
        })
        
        result = data_tools.analyze_data(analysis_input)
        result_json = json.loads(result)
        
        if result_json.get("success"):
            print("✅ Data analysis works correctly")
        else:
            print(f"❌ Data analysis failed: {result_json.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ DataTools test failed: {e}")
        return False
    
    try:
        from agent.tools.visualization_tools import VisualizationTools
        viz_tools = VisualizationTools()
        print("✅ VisualizationTools initialized successfully")
        
        # Test scatterplot creation
        scatter_input = json.dumps({
            "x_data": [1, 2, 3, 4, 5],
            "y_data": [2, 4, 6, 8, 10],
            "title": "Test Scatterplot",
            "x_label": "X",
            "y_label": "Y"
        })
        
        result = viz_tools.create_scatterplot(scatter_input)
        result_json = json.loads(result)
        
        if result_json.get("success"):
            print("✅ Visualization works correctly")
        else:
            print(f"❌ Visualization failed: {result_json.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ VisualizationTools test failed: {e}")
        return False
    
    return True

def test_api():
    """Test that the API can be imported and initialized"""
    print("\nTesting API...")
    
    try:
        # Import the handler function
        from api.main import handler, get_data_analyst_agent
        print("✅ API modules imported successfully")
        
        # Test agent initialization
        agent = get_data_analyst_agent()
        if agent is None:
            print("⚠️  Agent initialization returned None (expected if no env vars)")
        else:
            print("✅ Agent initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Vercel Deployment Configuration")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test agent import
    if not test_agent_import():
        all_passed = False
    
    # Test tools
    if not test_tools():
        all_passed = False
    
    # Test API
    if not test_api():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Deployment should work correctly.")
        print("\n📋 Next steps:")
        print("1. Set up environment variables in Vercel:")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_DEPLOYMENT_NAME")
        print("   - AZURE_OPENAI_API_VERSION")
        print("2. Deploy using: ./deploy-vercel.sh")
        print("3. Test the deployment with actual questions")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main() 