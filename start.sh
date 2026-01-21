#!/bin/bash

# Quick start script for RAG system

echo "=========================================="
echo "Agentic RAG System - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: Edit .env and add your GROQ_API_KEY"
    echo "   Get your free API key at: https://console.groq.com"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start services
echo "Starting services with Docker Compose..."
cd docker
docker-compose up --build -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "=========================================="
    echo "Access the application:"
    echo "  - API: http://localhost:8000"
    echo "  - Docs: http://localhost:8000/docs"
    echo "  - Weaviate: http://localhost:8080"
    echo "=========================================="
    echo ""
    echo "To test the system:"
    echo "  python test_system.py /path/to/your/document.pdf"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop:"
    echo "  docker-compose down"
else
    echo "❌ Services failed to start. Check logs with:"
    echo "   docker-compose logs"
fi
