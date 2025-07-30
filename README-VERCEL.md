# Data Analyst Agent - Vercel Deployment

This is a **lightweight deployment** of the Data Analyst Agent for Vercel serverless functions. Due to Vercel's 250MB size limit, this deployment excludes heavy data science libraries.

## 🚀 Quick Deploy

```bash
# Run the deployment script
./deploy-vercel.sh
```

## 📦 What's Included

- ✅ FastAPI server
- ✅ LangChain integration
- ✅ OpenAI/Azure OpenAI support
- ✅ Basic web scraping
- ✅ Health check endpoints
- ✅ CORS support

## ❌ What's NOT Included (Due to Size Limits)

- ❌ Pandas (data manipulation)
- ❌ NumPy (numerical computing)
- ❌ Matplotlib/Seaborn (plotting)
- ❌ Plotly (interactive plots)
- ❌ Scikit-learn (machine learning)
- ❌ SciPy (scientific computing)
- ❌ DuckDB (database)

## 🔧 Configuration

### Environment Variables

Set these in your Vercel dashboard:

```bash
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2023-12-01-preview
```

### API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /api/` - Process questions (limited functionality)

## 🏠 Local Development

For full functionality with all data science libraries, use the local version:

```bash
# Install full requirements
pip install -r requirements.txt

# Run locally
python local_main.py
```

## 📊 Size Optimization

The deployment uses:

1. **Minimal requirements** (`requirements-vercel.txt`)
2. **Lazy imports** - Heavy libraries only loaded when needed
3. **Excluded files** (`.vercelignore`)
4. **Optimized configuration** (`vercel.json`)

## 🔍 Troubleshooting

### Size Limit Exceeded

If you still get size limit errors:

1. Check `.vercelignore` excludes unnecessary files
2. Ensure `requirements-vercel.txt` is minimal
3. Consider removing more dependencies

### Import Errors

If you see import errors for data science libraries:

- This is expected - the lightweight deployment doesn't include them
- Use the local version for full functionality

## 📈 Performance

- **Cold start**: ~2-3 seconds
- **Warm start**: ~200-500ms
- **Memory usage**: ~50-100MB
- **Timeout**: 30 seconds

## 🔄 Updating

To update the deployment:

```bash
# Make your changes
git add .
git commit -m "Update deployment"

# Deploy
./deploy-vercel.sh
```

## 📝 Notes

- This deployment is optimized for **demonstration and basic functionality**
- For **production data analysis**, use the local version
- The API will return a message indicating limited functionality
- Consider using other platforms (Railway, Render, etc.) for full deployment 