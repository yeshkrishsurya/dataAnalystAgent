#!/bin/bash

# Data Analyst Agent - Vercel Deployment Script

echo "🚀 Starting Vercel deployment for Data Analyst Agent..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel..."
    vercel login
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Configure environment variables in Vercel dashboard:"
echo "   - AZURE_OPENAI_ENDPOINT"
echo "   - AZURE_OPENAI_API_KEY"
echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
echo "   - AZURE_OPENAI_API_VERSION"
echo ""
echo "2. Update gui_tester.py with your Vercel URL"
echo "3. Test your deployment with the health endpoint" 