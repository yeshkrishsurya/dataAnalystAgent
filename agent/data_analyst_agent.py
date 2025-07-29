import os
import json
import base64
import io
import logging
from typing import Any, Dict, List, Union
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain.tools import Tool
from agent.tools.data_tools import DataTools
from agent.tools.visualization_tools import VisualizationTools
from agent.tools.web_scraping_tools import WebScrapingTools

class DataAnalystAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Setting up Data Analyst Agent components...")
        
        self.llm = self._setup_llm()
        self.data_tools = DataTools()
        self.viz_tools = VisualizationTools()
        self.web_tools = WebScrapingTools()
        self.agent_executor = self._setup_agent()
        
        self.logger.info("Data Analyst Agent setup completed")
    
    def _setup_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM"""
        self.logger.info("Setting up Azure OpenAI LLM...")
        
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        self.logger.info(f"Azure endpoint: {endpoint}")
        self.logger.info(f"Deployment name: {deployment}")
        
        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
            deployment_name=deployment,
            temperature=0.1,
            max_tokens=4000
        )
    
    def _setup_agent(self) -> AgentExecutor:
        """Setup LangChain agent with tools"""
        self.logger.info("Setting up LangChain agent with tools...")
        
        tools = [
            Tool(
                name="scrape_wikipedia",
                description="Scrape data from Wikipedia URLs. Input should be a Wikipedia URL.",
                func=self.web_tools.scrape_wikipedia
            ),
            Tool(
                name="scrape_web",
                description="Scrape data from any web URL. Input should be a URL.",
                func=self.web_tools.scrape_web
            ),
            Tool(
                name="query_duckdb",
                description="Execute SQL queries on DuckDB. Input should be a SQL query string.",
                func=self.data_tools.query_duckdb
            ),
            Tool(
                name="analyze_data",
                description="Perform statistical analysis on data. Input should be a JSON string with data and analysis type.",
                func=self.data_tools.analyze_data
            ),
            Tool(
                name="create_plot",
                description="Create visualizations. Input should be a JSON string with plot type, data, and parameters.",
                func=self.viz_tools.create_plot
            ),
            Tool(
                name="create_scatterplot",
                description="Create scatterplot with regression line. Input should be JSON with x_data, y_data, title, labels.",
                func=self.viz_tools.create_scatterplot
            )
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data analyst agent that can source, prepare, analyze, and visualize data.

Your capabilities include:
1. Web scraping (especially Wikipedia and other data sources)
2. SQL queries on databases (DuckDB, S3 data)
3. Statistical analysis and correlations
4. Data visualization (plots, charts, scatterplots)

When answering questions:
- If multiple questions are asked, provide answers as a JSON array
- If a single question with multiple parts is asked, provide a JSON object
- For plots, return base64-encoded data URIs under 100,000 bytes
- Be precise with numerical answers
- Always validate your data sources and calculations

Use the available tools to:
1. Source the required data
2. Clean and prepare it
3. Perform the requested analysis
4. Create visualizations if needed
5. Format the final response correctly"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        
        self.logger.info(f"Agent created with {len(tools)} tools")
        
        return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)
    
    async def analyze(self, question: str) -> Union[List, Dict]:
        """Main analysis method that processes the question and returns results"""
        self.logger.info(f"Starting analysis for question: {question[:100]}...")
        
        try:
            # Run the agent
            self.logger.info("Invoking LangChain agent executor...")
            result = await self.agent_executor.ainvoke({"input": question})
            
            self.logger.info(f"Agent execution completed. Result keys: {list(result.keys())}")
            
            # Parse the output - try to extract JSON if present
            output = result["output"]
            self.logger.info(f"Raw output length: {len(output)} characters")
            self.logger.info(f"Raw output preview: {output[:200]}...")
            
            # Try to parse as JSON
            try:
                parsed_result = json.loads(output)
                self.logger.info(f"Successfully parsed output as JSON: {type(parsed_result)}")
                return parsed_result
            except json.JSONDecodeError as jde:
                self.logger.warning(f"Failed to parse output as JSON: {str(jde)}")
                # If not valid JSON, return as string
                return {"result": output}
                
        except Exception as e:
            self.logger.error(f"Analysis failed with exception: {str(e)}")
            self.logger.exception("Full exception traceback:")
            return {"error": f"Analysis failed: {str(e)}"}