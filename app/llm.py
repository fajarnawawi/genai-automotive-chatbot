"""
LLM Module - Vertex AI Gemini Integration
Handles language model initialization and configuration
"""

import logging
from typing import Optional
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from langchain_google_vertexai import ChatVertexAI
from app.config import config

logger = logging.getLogger(__name__)


class LLMManager:
    """Manager for Language Model interactions"""
    
    def __init__(self):
        self._llm: Optional[ChatVertexAI] = None
        self._initialized = False
    
    def initialize_vertex_ai(self) -> None:
        """Initialize Vertex AI with project configuration"""
        if not self._initialized:
            try:
                vertexai.init(
                    project=config.PROJECT_ID,
                    location=config.LOCATION,
                )
                self._initialized = True
                logger.info(
                    f"Vertex AI initialized: {config.PROJECT_ID} ({config.LOCATION})"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {str(e)}")
                raise
    
    def get_llm(self) -> ChatVertexAI:
        """
        Get or create LangChain ChatVertexAI instance for Gemini 2.0
        
        Returns:
            ChatVertexAI: Configured language model
        """
        if self._llm is None:
            try:
                # Ensure Vertex AI is initialized
                self.initialize_vertex_ai()
                
                # Create LangChain ChatVertexAI with Gemini 2.0
                self._llm = ChatVertexAI(
                    model_name=config.GEMINI_MODEL,
                    temperature=config.GEMINI_TEMPERATURE,
                    max_output_tokens=config.GEMINI_MAX_OUTPUT_TOKENS,
                    top_p=config.GEMINI_TOP_P,
                    top_k=config.GEMINI_TOP_K,
                    project=config.PROJECT_ID,
                    location=config.LOCATION,
                    verbose=True,
                    # Gemini 2.0 specific settings
                    convert_system_message_to_human=False,  # Keep system messages
                )
                
                logger.info(f"LLM initialized: {config.GEMINI_MODEL}")
                
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
                raise
        
        return self._llm
    
    def test_llm(self) -> dict:
        """
        Test LLM with a simple prompt
        
        Returns:
            dict: Test results
        """
        try:
            llm = self.get_llm()
            response = llm.invoke("Say 'Hello' if you can hear me.")
            
            return {
                "status": "success",
                "model": config.GEMINI_MODEL,
                "response": response.content if hasattr(response, 'content') else str(response),
            }
        except Exception as e:
            logger.error(f"LLM test failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    def get_generation_config(self) -> dict:
        """
        Get current generation configuration
        
        Returns:
            dict: Current configuration parameters
        """
        return {
            "model": config.GEMINI_MODEL,
            "temperature": config.GEMINI_TEMPERATURE,
            "max_output_tokens": config.GEMINI_MAX_OUTPUT_TOKENS,
            "top_p": config.GEMINI_TOP_P,
            "top_k": config.GEMINI_TOP_K,
        }


# Global LLM instance
_llm_instance: Optional[LLMManager] = None


def get_llm_instance() -> LLMManager:
    """
    Get singleton LLM manager instance
    
    Returns:
        LLMManager: LLM manager instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMManager()
    return _llm_instance


def initialize_llm() -> dict:
    """
    Initialize LLM and return status
    
    Returns:
        dict: Initialization status
    """
    try:
        llm_manager = get_llm_instance()
        llm_manager.initialize_vertex_ai()
        return {
            "status": "success",
            "model": config.GEMINI_MODEL,
            "location": config.LOCATION,
        }
    except Exception as e:
        logger.error(f"LLM initialization failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
