from typing import List
from mistralai import Mistral, UserMessage, SystemMessage
from services.qdrant import qdrant_client, model
from config.config import settings
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
import logging


class RAGAgent:
    def __init__(self):
        self.client = Mistral(api_key = settings.MISTRAL_API_KEY)
        self.collection_name = "web_scraped_data"
        self.model_name = "mistral-medium"  

        try:
            nltk.download('punkt')
            nltk.download('punkt_tab')

        except :
            logging.error("NLTK Error")

        self.summarizer = LsaSummarizer(Stemmer('english'))
        self.summarizer.stop_words = get_stop_words('english')
        
    def _summarize_content(self, content: str, sentences_count: int = 2) -> str:
        """Summarize content using LSA (Latent Semantic Analysis)"""
        try:
            logging.info("Going to Parser")
            parser = PlaintextParser.from_string(content, Tokenizer("english"))
            logging.info("Going to summarizer")
            summary = self.summarizer(parser.document, sentences_count)
            return " ".join([str(sentence) for sentence in summary])
        except Exception as e:
            print(f"Summarization failed: {str(e)}")
            return content[:300] + "..."  

    def _get_relevant_context(self, query: str, session_id : str, limit: int = 4) -> List[str]:
        """Retrieve and summarize relevant documents from Qdrant"""
        query_vector = model.encode(query).tolist()
        
        search_result = qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter={
            "must": [
                {"key": "session_id", "match": {"value": session_id}}
            ]
            },
            limit=limit
        )
        
        contexts = []
        for result in search_result:
            summarized_content = self._summarize_content(result.payload['content'])
            contexts.append(f"Content: {summarized_content}\nSource: {result.payload['url']}")
        
        return contexts

    def _create_prompt(self, query: str, contexts: List[str]) -> str:
        """Create a prompt with retrieved context"""
        context_str = "\n\n".join(contexts)
        return f"""Based on these Sources, answer question:
{context_str}

Q: {query}

A:"""

    async def get_response(self, query: str, session_id : str) -> str:
        """Get response from Mistral AI using RAG"""
        try:
            # Get relevant context from vector store
            contexts = self._get_relevant_context(query, session_id=session_id)
            
            if not contexts:
                return "I couldn't find any relevant information to answer your question."
            
            # Create messages for chat completion
            messages = [ 
                SystemMessage(content = "You are a helpful assistant that answers questions based on the provided context"),
                UserMessage(content = self._create_prompt(query, contexts))
            ]
            
            # Get response from Mistral
            chat_response = await self.client.chat.complete_async(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return chat_response.choices[0].message.content
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def stream_response(self, query: str):
        """Stream response from Mistral AI using RAG"""
        try:
            contexts = self._get_relevant_context(query)
            
            if not contexts:
                yield "I couldn't find any relevant information to answer your question."
                return
            
            messages = [ 
                SystemMessage(content = "You are a helpful assistant that answers questions based on the provided context"),
                UserMessage(content = self._create_prompt(query, contexts))
            ]
            
            stream = await self.client.chat.stream_async(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            async for chunk in stream:
                if chunk.data.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"An error occurred: {str(e)}"