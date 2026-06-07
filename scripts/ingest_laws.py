#!/usr/bin/env python3
"""Run this after installing ai-services/requirements.txt to populate ChromaDB."""
import sys, os

# Add ai-services to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../ai-services"))

from rag.indexer import ingest

if __name__ == "__main__":
    ingest()
