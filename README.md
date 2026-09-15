# AI Video and Meeting Assistant

A Streamlit application that turns YouTube videos, uploaded files, and meeting audio into searchable AI-generated briefs using a FastAPI backend.

## Features

- YouTube URL and local file processing
- Audio and video transcription with Whisper
- English and Hinglish transcript support
- AI-generated titles and summaries
- Meeting action-item extraction
- Decision and open-question extraction
- RAG-powered questions over transcript content
- Chroma vector retrieval
- Downloadable meeting briefs
- FastAPI backend for analysis and question answering
- REST API endpoints for analysis and transcript queries
- Responsive light and dark Streamlit interface

## Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  | POST /analyze
  v
FastAPI Backend
  |
  v
AI Processing Pipeline
  |
  +-- Whisper Transcription
  +-- Mistral AI
  +-- Text Extraction
  +-- ChromaDB / RAG
  |
  v
Analysis Results
  |
  v
Streamlit Frontend
  |
  | POST /analyses/{analysis_id}/ask
  v
FastAPI RAG Question Answering
