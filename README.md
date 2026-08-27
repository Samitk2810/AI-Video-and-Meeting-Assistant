# AI Video and Meeting Assistant

A Streamlit application that turns YouTube videos, uploaded files, and meeting audio into searchable AI-generated briefs.

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
- Responsive light and dark Streamlit interface

## Tech Stack

Python, Streamlit, OpenAI Whisper, Mistral AI, LangChain, ChromaDB, Sentence Transformers, and FFmpeg.

## Setup

```bash
git clone https://github.com/Samitk2810/AI-Video-and-Meeting-Assistant.git
cd AI-Video-and-Meeting-Assistant
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

Never commit `.env` or your API key.

## Run

```bash
streamlit run app.py
```

Choose a source in the sidebar, select the transcript language, and click **Analyze**. Meeting audio enables the full extraction workflow; other sources provide title, summary, and transcript chat.
