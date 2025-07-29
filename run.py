#!/usr/bin/env python3
"""
Simple test runner for the Data Analyst Agent
"""
import asyncio
import json
from agent.data_analyst_agent import DataAnalystAgent

async def test_agent():
    """Test the agent with sample questions"""
    agent = DataAnalystAgent()
    
    # Test question 1: Simple analysis
    test_question = """
    Create a simple dataset with numbers 1 through 10 and their squares.
    Calculate the correlation between the numbers and their squares.
    """
    
    print("Testing agent with simple question...")
    print(f"Question: {test_question}")
    
    try:
        result = await agent.analyze(test_question)
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent())