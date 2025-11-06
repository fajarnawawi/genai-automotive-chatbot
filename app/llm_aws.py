"""
LLM Module - Amazon Bedrock Integration
Handles language model initialization and configuration with Claude
"""

import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrock
from app.config_aws import config_aws

logger = logging.getLogger(__name__)


class LLMManagerAWS:
    """Manager for Language Model interactions using Amazon Bedrock"""

    def __init__(self):
        self._llm: Optional[ChatBedrock] = None
        self._bedrock_client: Optional[boto3.client] = None
        self._initialized = False

    def initialize_bedrock(self) -> None:
        """Initialize Bedrock client with AWS configuration"""
        if not self._initialized:
            try:
                self._bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=config_aws.AWS_REGION
                )
                self._initialized = True
                logger.info(
                    f"Bedrock initialized in region: {config_aws.AWS_REGION}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock: {str(e)}")
                raise

    def get_llm(self) -> ChatBedrock:
        """
        Get or create LangChain ChatBedrock instance for Claude

        Returns:
            ChatBedrock: Configured language model
        """
        if self._llm is None:
            try:
                # Ensure Bedrock is initialized
                self.initialize_bedrock()

                # Create LangChain ChatBedrock with Claude
                self._llm = ChatBedrock(
                    model_id=config_aws.BEDROCK_MODEL_ID,
                    client=self._bedrock_client,
                    region_name=config_aws.AWS_REGION,
                    model_kwargs={
                        "temperature": config_aws.BEDROCK_TEMPERATURE,
                        "top_p": config_aws.BEDROCK_TOP_P,
                        "top_k": config_aws.BEDROCK_TOP_K,
                        "max_tokens": config_aws.BEDROCK_MAX_TOKENS,
                    },
                    streaming=False,
                    verbose=True,
                )

                logger.info(f"LLM initialized: {config_aws.BEDROCK_MODEL_ID}")

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
                "model": config_aws.BEDROCK_MODEL_ID,
                "response": response.content if hasattr(response, 'content') else str(response),
            }
        except Exception as e:
            logger.error(f"LLM test failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
            }

    def list_available_models(self) -> dict:
        """
        List available Bedrock foundation models

        Returns:
            dict: Available models information
        """
        try:
            bedrock_client = boto3.client(
                service_name='bedrock',
                region_name=config_aws.AWS_REGION
            )

            response = bedrock_client.list_foundation_models()

            claude_models = [
                model for model in response.get('modelSummaries', [])
                if 'claude' in model.get('modelId', '').lower()
            ]

            return {
                "status": "success",
                "claude_models": [
                    {
                        "model_id": model.get('modelId'),
                        "model_name": model.get('modelName'),
                        "provider": model.get('providerName'),
                    }
                    for model in claude_models
                ],
            }
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
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
            "model": config_aws.BEDROCK_MODEL_ID,
            "temperature": config_aws.BEDROCK_TEMPERATURE,
            "max_tokens": config_aws.BEDROCK_MAX_TOKENS,
            "top_p": config_aws.BEDROCK_TOP_P,
            "top_k": config_aws.BEDROCK_TOP_K,
        }

    def invoke_with_retries(self, prompt: str, max_retries: int = 3) -> dict:
        """
        Invoke LLM with automatic retries for throttling

        Args:
            prompt: Input prompt
            max_retries: Maximum number of retry attempts

        Returns:
            dict: Response or error
        """
        import time

        for attempt in range(max_retries):
            try:
                llm = self.get_llm()
                response = llm.invoke(prompt)

                return {
                    "status": "success",
                    "response": response.content if hasattr(response, 'content') else str(response),
                    "attempts": attempt + 1,
                }

            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')

                # Retry on throttling errors
                if error_code == 'ThrottlingException' and attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Throttled. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Bedrock API error: {str(e)}")
                    return {
                        "status": "error",
                        "error": str(e),
                        "error_code": error_code,
                    }

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return {
                    "status": "error",
                    "error": str(e),
                }

        return {
            "status": "error",
            "error": "Max retries exceeded",
        }


# Global LLM instance
_llm_instance: Optional[LLMManagerAWS] = None


def get_llm_instance() -> LLMManagerAWS:
    """
    Get singleton LLM manager instance

    Returns:
        LLMManagerAWS: LLM manager instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMManagerAWS()
    return _llm_instance


def initialize_llm() -> dict:
    """
    Initialize LLM and return status

    Returns:
        dict: Initialization status
    """
    try:
        llm_manager = get_llm_instance()
        llm_manager.initialize_bedrock()
        return {
            "status": "success",
            "model": config_aws.BEDROCK_MODEL_ID,
            "region": config_aws.AWS_REGION,
        }
    except Exception as e:
        logger.error(f"LLM initialization failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
