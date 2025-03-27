# SmartAgent - AI-Powered Documentation Chat System

## Overview

SmartAgent is a modern web application that transforms documentation into an interactive chat experience. Using advanced AI and natural language processing, it allows users to have natural conversations with their documentation.

## Features

- 🔍 **Smart Web Scraping**: Automatically extracts content from documentation websites
- 🤖 **AI-Powered Chat**: Natural language interaction with documentation content
- 🔒 **URL Safety Checks**: Built-in protection against unsafe or malicious websites
- ⚡ **Real-time Updates**: Live progress tracking for content processing
- 🌐 **Multi-user Support**: Separate chat sessions for different users
- 🎨 **Modern Dark Theme**: Clean, high-contrast interface with neon accents

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MongoDB, Qdrant Vector Database
- **AI/ML**: Sentence Transformers, Mistral, Sumy, NLTK, BeautifulSoup
- **Security**: Google Safe Browsing API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SmartAgent.git
cd SmartAgent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
MONGODB_URI=your_mongodb_uri
GOOGLE_SAFE_BROWSING_API_KEY=your_api_key
QDRANT_HOST=your_qdrant_host
QDRANT_PORT=your_qdrant_port
MISTRAL_API_KEY=your_mistralai_api_key
```

## Usage

1. Start the server:
```bash
python main_.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Enter a documentation URL and start chatting!

## Project Structure

```
SmartAgent/
├── api/
│   ├── chat_endpoint.py
│   └── scraper.py
├── services/
│   ├── utility.py
│   └── scraper.py
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── chat.html
│   ├── home.html
│   └── how_it_works.html
└── main_.py
```

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Requirements

- Python 3.9+
- MongoDB
- Qdrant Vector Database
- Google Safe Browsing API key

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the amazing web framework
- LangChain for AI capabilities
- Sentence Transformers for text embeddings
- MongoDB and Qdrant for storage solutions

## Support

For support, please open an issue in the GitHub repository.

---

Built with ❤️ using Python and AI