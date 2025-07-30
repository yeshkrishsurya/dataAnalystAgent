#!/bin/bash

echo "🚀 Deploying Data Analyst Agent to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "npm install -g vercel"
    exit 1
fi

# Create a temporary requirements.txt for deployment
echo "📦 Creating minimal requirements for Vercel deployment..."
cp requirements-vercel.txt requirements.txt

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

# Restore original requirements.txt
echo "🔄 Restoring original requirements.txt..."
git checkout requirements.txt

echo "✅ Deployment completed!"
echo "📝 Note: This is a lightweight deployment. For full data analysis features, use the local version." 