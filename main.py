from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from agent.data_analyst_agent import DataAnalystAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_analyst_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Analyst Agent API", version="1.0.0")

# Initialize the agent
logger.info("Initializing Data Analyst Agent...")
agent = DataAnalystAgent()
logger.info("Data Analyst Agent initialized successfully")

@app.post("/api/")
async def analyze_data(file: UploadFile = File(...)):
    """
    Main API endpoint that accepts a file containing a data analysis task
    and returns the analysis results as JSON.
    """
    start_time = time.time()
    request_id = f"req_{int(start_time)}"
    
    logger.info(f"[{request_id}] New API request received")
    logger.info(f"[{request_id}] File details - name: {file.filename}, content_type: {file.content_type}")
    
    try:
        # Read the uploaded file content
        logger.info(f"[{request_id}] Reading uploaded file content...")
        content = await file.read()
        question = content.decode('utf-8').strip()
        
        logger.info(f"[{request_id}] File content length: {len(content)} bytes")
        logger.info(f"[{request_id}] Question preview: {question[:200]}...")
        
        if not question:
            logger.warning(f"[{request_id}] Empty question file received")
            raise HTTPException(status_code=400, detail="Empty question file")
        
        # Process the question using the data analyst agent
        logger.info(f"[{request_id}] Starting analysis with Data Analyst Agent...")
        result = await agent.analyze(question)
        
        processing_time = time.time() - start_time
        logger.info(f"[{request_id}] Analysis completed successfully in {processing_time:.2f}s")
        logger.info(f"[{request_id}] Result type: {type(result)}, length: {len(str(result))}")
        
        return JSONResponse(content=result)
        
    except HTTPException as he:
        logger.error(f"[{request_id}] HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"[{request_id}] Analysis failed after {processing_time:.2f}s: {str(e)}")
        logger.exception(f"[{request_id}] Full exception details:")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)