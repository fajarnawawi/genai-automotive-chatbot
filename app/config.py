# Configuration file for Automotive Sales Analytics Chatbot
# All sensitive values should be set via environment variables

import os
from typing import Optional
from dotenv import load_dotenv 

# Load environment variables from .env file
load_dotenv()  # ADD THIS LINE

class Config:
    """Application configuration"""
    
    # Google Cloud Project Configuration
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "YOUR_PROJECT_ID")
    LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    
    # BigQuery Configuration
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "automotive_data")
    BIGQUERY_LOCATION: str = os.getenv("BIGQUERY_LOCATION", "US")
    
    # Vertex AI Configuration
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite-001")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    GEMINI_MAX_OUTPUT_TOKENS: int = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
    GEMINI_TOP_P: float = float(os.getenv("GEMINI_TOP_P", "0.95"))
    GEMINI_TOP_K: int = int(os.getenv("GEMINI_TOP_K", "40"))
    
    # Authentication
    # For local development: set GOOGLE_APPLICATION_CREDENTIALS
    # For Cloud Run: uses default service account
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Application Configuration
    APP_TITLE: str = "Automotive Sales Analytics Chatbot"
    APP_ICON: str = "🚗"
    MAX_CHAT_HISTORY: int = int(os.getenv("MAX_CHAT_HISTORY", "10"))
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: Optional[str] = os.getenv("LANGCHAIN_PROJECT")
    
    # SQL Agent Configuration
    SQL_AGENT_MAX_ITERATIONS: int = int(os.getenv("SQL_AGENT_MAX_ITERATIONS", "15"))
    SQL_AGENT_MAX_EXECUTION_TIME: int = int(os.getenv("SQL_AGENT_MAX_EXECUTION_TIME", "100"))
    SQL_TOP_K_RESULTS: int = int(os.getenv("SQL_TOP_K_RESULTS", "10"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        required_fields = {
            "PROJECT_ID": cls.PROJECT_ID,
            "BIGQUERY_DATASET": cls.BIGQUERY_DATASET,
        }
        
        missing_fields = [
            field for field, value in required_fields.items()
            if not value or value.startswith("YOUR_")
        ]
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Please set the appropriate environment variables."
            )
    
    @classmethod
    def get_bigquery_uri(cls) -> str:
        """Get the BigQuery connection URI"""
        return f"bigquery://{cls.PROJECT_ID}/{cls.BIGQUERY_DATASET}"
    
    @classmethod
    def display_config(cls) -> dict:
        """Get configuration for display (without sensitive data)"""
        return {
            "Project ID": cls.PROJECT_ID,
            "Location": cls.LOCATION,
            "Dataset": cls.BIGQUERY_DATASET,
            "Model": cls.GEMINI_MODEL,
            "Temperature": cls.GEMINI_TEMPERATURE,
        }


# Initialize and validate config on import
config = Config()
