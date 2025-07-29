# Data Analyst Agent

A generalist data analysis agent built with LangChain and Azure OpenAI API. This API can source, prepare, analyze, and visualize any data.

## Features

- **Data Sourcing**: Web scraping (Wikipedia, general websites), SQL queries on DuckDB
- **Data Analysis**: Statistical analysis, correlations, regression analysis
- **Data Visualization**: Charts, plots, scatterplots with regression lines
- **LLM Integration**: Uses Azure OpenAI via LangChain for intelligent data analysis

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2023-12-01-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   ```

3. **Run the API**:
   ```bash
   python local_main.py
   ```
   
   The API will be available at `http://localhost:8000`

## Usage

Send POST requests to `/api/` with a file containing your data analysis question:

```bash
curl "http://localhost:8000/api/" -F "file=@question.txt"
```

### Example Questions

The agent can handle complex data analysis tasks like:

1. **Web Scraping & Analysis**:
   - Scrape Wikipedia tables
   - Perform statistical analysis on the data
   - Answer specific questions about the data

2. **Database Queries**:
   - Execute SQL queries on DuckDB
   - Analyze large datasets (e.g., S3 data)
   - Generate insights and visualizations

3. **Data Visualization**:
   - Create scatterplots with regression lines
   - Generate charts and graphs
   - Return plots as base64-encoded data URIs

## API Endpoints

- `POST /api/` - Main analysis endpoint
- `GET /health` - Health check

## Architecture

- **FastAPI**: Web framework for the API
- **LangChain**: Agent framework with tool integration
- **Azure OpenAI**: LLM for intelligent analysis
- **Tools**:
  - `WebScrapingTools`: Wikipedia and general web scraping
  - `DataTools`: Statistical analysis and DuckDB queries
  - `VisualizationTools`: Chart and plot generation

## Deployment

### Vercel Deployment

This project is configured for easy deployment to Vercel as a serverless API. See [README-VERCEL.md](README-VERCEL.md) for detailed deployment instructions.

Quick deployment:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
./deploy-vercel.sh
```

### Local Development

For local development, use the original setup:
```bash
pip install -r requirements.txt
python local_main.py
```

## License

MIT License - see LICENSE file for details.