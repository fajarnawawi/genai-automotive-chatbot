# Configuration file for Automotive Sales Analytics Chatbot - AWS Version
# All sensitive values should be set via environment variables

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigAWS:
    """AWS Application configuration"""

    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCOUNT_ID: str = os.getenv("AWS_ACCOUNT_ID", "YOUR_ACCOUNT_ID")

    # Amazon Redshift Configuration
    REDSHIFT_HOST: str = os.getenv("REDSHIFT_HOST", "your-cluster.region.redshift.amazonaws.com")
    REDSHIFT_PORT: int = int(os.getenv("REDSHIFT_PORT", "5439"))
    REDSHIFT_DATABASE: str = os.getenv("REDSHIFT_DATABASE", "automotive_data")
    REDSHIFT_SCHEMA: str = os.getenv("REDSHIFT_SCHEMA", "public")
    REDSHIFT_USER: str = os.getenv("REDSHIFT_USER", "admin")
    REDSHIFT_PASSWORD: str = os.getenv("REDSHIFT_PASSWORD", "")
    # Alternative: Use IAM authentication
    REDSHIFT_USE_IAM: bool = os.getenv("REDSHIFT_USE_IAM", "false").lower() == "true"
    REDSHIFT_CLUSTER_IDENTIFIER: str = os.getenv("REDSHIFT_CLUSTER_IDENTIFIER", "automotive-cluster")

    # Amazon Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    BEDROCK_TEMPERATURE: float = float(os.getenv("BEDROCK_TEMPERATURE", "0.1"))
    BEDROCK_MAX_TOKENS: int = int(os.getenv("BEDROCK_MAX_TOKENS", "2048"))
    BEDROCK_TOP_P: float = float(os.getenv("BEDROCK_TOP_P", "0.95"))
    BEDROCK_TOP_K: int = int(os.getenv("BEDROCK_TOP_K", "250"))

    # Authentication
    # For local development: set AWS credentials via ~/.aws/credentials or environment variables
    # For ECS/Lambda: uses IAM role automatically
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = os.getenv("AWS_SESSION_TOKEN")  # For temporary credentials

    # Application Configuration
    APP_TITLE: str = "Automotive Sales Analytics Chatbot (AWS)"
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
    CLOUDWATCH_LOG_GROUP: str = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/automotive-chatbot")
    CLOUDWATCH_LOG_STREAM: str = os.getenv("CLOUDWATCH_LOG_STREAM", "app")

    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        required_fields = {
            "AWS_REGION": cls.AWS_REGION,
            "REDSHIFT_HOST": cls.REDSHIFT_HOST,
            "REDSHIFT_DATABASE": cls.REDSHIFT_DATABASE,
        }

        missing_fields = [
            field for field, value in required_fields.items()
            if not value or value.startswith("YOUR_") or value.startswith("your-")
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Please set the appropriate environment variables."
            )

        # Validate authentication
        if not cls.REDSHIFT_USE_IAM and not cls.REDSHIFT_PASSWORD:
            raise ValueError(
                "REDSHIFT_PASSWORD is required when not using IAM authentication. "
                "Set REDSHIFT_USE_IAM=true to use IAM authentication instead."
            )

    @classmethod
    def get_redshift_uri(cls) -> str:
        """Get the Redshift connection URI"""
        if cls.REDSHIFT_USE_IAM:
            # For IAM authentication, password will be generated at runtime
            return f"postgresql+psycopg2://{cls.REDSHIFT_USER}@{cls.REDSHIFT_HOST}:{cls.REDSHIFT_PORT}/{cls.REDSHIFT_DATABASE}"
        else:
            # Standard authentication with password
            return f"postgresql+psycopg2://{cls.REDSHIFT_USER}:{cls.REDSHIFT_PASSWORD}@{cls.REDSHIFT_HOST}:{cls.REDSHIFT_PORT}/{cls.REDSHIFT_DATABASE}"

    @classmethod
    def display_config(cls) -> dict:
        """Get configuration for display (without sensitive data)"""
        return {
            "AWS Region": cls.AWS_REGION,
            "Redshift Cluster": cls.REDSHIFT_CLUSTER_IDENTIFIER,
            "Database": cls.REDSHIFT_DATABASE,
            "Schema": cls.REDSHIFT_SCHEMA,
            "Bedrock Model": cls.BEDROCK_MODEL_ID,
            "Temperature": cls.BEDROCK_TEMPERATURE,
        }


# Initialize and validate config on import
config_aws = ConfigAWS()
