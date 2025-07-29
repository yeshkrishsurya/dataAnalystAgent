# Data Analyst Agent - Vercel Deployment

This guide explains how to deploy the Data Analyst Agent to Vercel as a serverless API.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Environment Variables**: You'll need to configure your Azure OpenAI credentials

## Deployment Steps

### 1. Prepare Your Repository

The project is already configured for Vercel with the following files:
- `vercel.json` - Vercel configuration
- `api/main.py` - Serverless function entry point
- `requirements-vercel.txt` - Python dependencies
- `runtime.txt` - Python version specification

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from your project directory
vercel

# Follow the prompts to configure your project
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your Git repository
4. Configure the project settings

### 3. Configure Environment Variables

In your Vercel project dashboard, go to Settings → Environment Variables and add:

```
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2023-12-01-preview
```

### 4. Update GUI Tester

After deployment, update the `gui_tester.py` file with your Vercel URL:

```python
self.api_base_url = "https://your-vercel-app.vercel.app"
```

## API Endpoints

Once deployed, your API will be available at:

- **Root**: `https://your-vercel-app.vercel.app/`
- **Health Check**: `https://your-vercel-app.vercel.app/health`
- **Main API**: `https://your-vercel-app.vercel.app/api/`

## Important Notes

### Cold Starts
- The agent is initialized lazily on the first request to handle cold starts
- Subsequent requests will be faster as the agent stays in memory

### Function Timeout
- Vercel has a 10-second timeout for Hobby plans
- Pro plans have up to 60-second timeout
- Consider upgrading if you need longer processing times

### Memory Limits
- Hobby: 1024 MB
- Pro: 3008 MB
- Enterprise: 3008 MB

### File Size Limits
- Request body: 4.5 MB (Hobby), 32 MB (Pro)
- Response body: 4.5 MB (Hobby), 32 MB (Pro)

## Testing Your Deployment

1. **Health Check**:
   ```bash
   curl https://your-vercel-app.vercel.app/health
   ```

2. **Using the GUI Tester**:
   - Update the URL in `gui_tester.py`
   - Run the GUI tester
   - Test with sample questions

3. **Direct API Call**:
   ```bash
   curl -X POST https://your-vercel-app.vercel.app/api/ \
     -F "file=@your_question.txt"
   ```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements-vercel.txt`
2. **Environment Variables**: Verify all Azure OpenAI credentials are set
3. **Timeout Errors**: Consider upgrading to Pro plan for longer timeouts
4. **Memory Issues**: Optimize your code or upgrade to Pro plan

### Logs
- Check Vercel function logs in the dashboard
- Use `vercel logs` command for CLI access

## Local Development

For local development, you can still use the original `local_main.py`:

```bash
pip install -r requirements.txt
python local_main.py
```

## Performance Optimization

1. **Lazy Loading**: The agent is initialized only when needed
2. **Connection Pooling**: Reuse database connections when possible
3. **Caching**: Consider implementing response caching for repeated queries
4. **Image Optimization**: Ensure base64 images are under size limits

## Security Considerations

1. **CORS**: Configure proper CORS origins for production
2. **Rate Limiting**: Consider implementing rate limiting
3. **Input Validation**: Validate all inputs thoroughly
4. **API Keys**: Never expose API keys in client-side code

## Cost Optimization

1. **Function Duration**: Optimize code to reduce execution time
2. **Memory Usage**: Use only necessary dependencies
3. **Request Volume**: Monitor usage and optimize accordingly 