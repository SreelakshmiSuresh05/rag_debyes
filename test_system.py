#!/usr/bin/env python3
"""
Test script for the RAG system.
Run this after starting the Docker containers.
"""

import requests
import sys
from pathlib import Path

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_ingest(pdf_path: str):
    """Test document ingestion."""
    print(f"Testing document ingestion with {pdf_path}...")
    
    if not Path(pdf_path).exists():
        print(f"Error: File {pdf_path} not found")
        return False
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        response = requests.post(f"{API_URL}/ingest", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_query(question: str):
    """Test query endpoint."""
    print(f"Testing query: '{question}'...")
    
    payload = {"question": question}
    response = requests.post(f"{API_URL}/query", json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Question: {result['question']}")
        print(f"Is Complex: {result['is_complex']}")
        if result['sub_questions']:
            print(f"Sub-questions: {result['sub_questions']}")
        print(f"Answer: {result['answer']}")
        print(f"Sources: {len(result['sources'])} chunks")
        print(f"Metadata: {result['metadata']}\n")
    else:
        print(f"Error: {response.text}\n")
    
    return response.status_code == 200


def main():
    """Run tests."""
    print("=" * 60)
    print("RAG System Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    if not test_health():
        print("❌ Health check failed. Is the server running?")
        sys.exit(1)
    print("✅ Health check passed\n")
    
    # Test 2: Ingest (if PDF path provided)
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if test_ingest(pdf_path):
            print("✅ Document ingestion passed\n")
        else:
            print("❌ Document ingestion failed\n")
    else:
        print("⚠️  Skipping ingestion test (no PDF provided)\n")
        print("Usage: python test_system.py <path_to_pdf>\n")
    
    # Test 3: Simple query
    if test_query("What is the main topic?"):
        print("✅ Simple query passed\n")
    else:
        print("❌ Simple query failed\n")
    
    # Test 4: Complex query
    if test_query("What are the key findings and main recommendations?"):
        print("✅ Complex query passed\n")
    else:
        print("❌ Complex query failed\n")
    
    print("=" * 60)
    print("Test suite complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
