"""
Automotive Sales Analytics Chatbot
Application Package
"""

__version__ = "1.0.0"
__author__ = "AI Engineering Team"

from app.config import config
from app.database import get_database_instance, initialize_database
from app.llm import get_llm_instance, initialize_llm
from app.agent import get_agent_instance, query_database, initialize_agent

__all__ = [
    "config",
    "get_database_instance",
    "initialize_database",
    "get_llm_instance",
    "initialize_llm",
    "get_agent_instance",
    "query_database",
    "initialize_agent",
]
