#!/bin/bash

# Setup script for local development

echo "🚀 Setting up Medical Record Translator for local development..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key!"
    echo "   Run: nano .env"
    echo ""
fi

# Stop any running containers
echo "🛑 Stopping any existing containers..."
docker-compose down

# Rebuild containers
echo "🔨 Rebuilding containers with updated requirements..."
docker-compose build --no-cache backend

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
echo ""

# Check backend
if curl -f http://localhost:8000/api/v1/translate/health 2>/dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding. Check logs with: docker-compose logs backend"
fi

# Check frontend
if curl -f http://localhost:3000/health 2>/dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding. Check logs with: docker-compose logs frontend"
fi

echo ""
echo "📋 Quick Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo ""

# Check if OpenAI key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  WARNING: OpenAI API key is not set in .env file!"
    echo "   Edit .env and add your OpenAI API key, then run:"
    echo "   docker-compose restart backend"
else
    echo "🎉 Setup complete! Access the application at:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
fi