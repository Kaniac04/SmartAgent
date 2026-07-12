[English] | [日本語](README.ja.md)

# SmartAgent - AI-Powered Documentation Chat System

SmartAgent is a modern web application that transforms static documentation into an interactive chat experience. By leveraging Retrieval-Augmented Generation (RAG), it allows users to query documentation using natural language.

---

## Features

- Smart Web Scraping: Automatically extracts and cleans content from documentation websites.
- RAG Architecture: Uses Qdrant Vector Database for lightning-fast semantic search.
- AI-Powered Chat: Natural language interaction powered by Mistral AI.
- URL Safety: Integrated Google Safe Browsing API to protect against malicious links.
- Real-time Tracking: Live progress updates during documentation indexing.
- Modern UI: Sleek dark-themed interface with neon accents and responsive design.

---

## Tech Stack

- Backend: FastAPI (Python 3.9+)
- Vector Store: Qdrant
- Database: MongoDB (Session & Metadata management)
- Embeddings: Sentence Transformers
- LLM: Mistral AI
- Security: Google Safe Browsing API

---

## How It Works

1. Ingestion: User provides a documentation URL.
2. Scraping: The system crawls the site and extracts meaningful text.
3. Indexing: Content is chunked, converted into embeddings, and stored in Qdrant.
4. Retrieval: When a question is asked, the system finds relevant context from the vector store.
5. Generation: Mistral AI generates a precise answer based on the retrieved context.

---

## Installation

### Prerequisites
- Python 3.9 or higher
- A running MongoDB instance
- A Qdrant instance

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SmartAgent.git
   cd SmartAgent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Environment Variables:
   Create a .env file in the root directory:
   ```env
   MONGODB_URI=your_mongodb_uri
   GOOGLE_SAFE_BROWSING_API_KEY=your_api_key
   QDRANT_HOST=your_qdrant_host
   QDRANT_PORT=6333
   MISTRAL_API_KEY=your_mistralai_api_key
   ```

---

## Usage

1. Launch the server:
   ```bash
   python main_.py
   ```

2. Access the Web UI:
   Open http://localhost:8000 in your browser.

---

## Project Structure

```text
SmartAgent/
├── api/                # API Endpoints (Chat & Scraper)
├── services/           # Business Logic (RAG, Scraping, Utils)
├── static/             # CSS & JS assets
├── templates/          # HTML Templates (Jinja2)
└── main_.py            # Application Entry Point
```

---

## License

Distributed under the MIT License. See LICENSE for more information.

---

Disclaimer: This tool is for educational purposes. Always ensure you have permission to scrape documentation from websites.
