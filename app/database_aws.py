"""
Amazon Redshift Database Connection Module
Handles connection to Amazon Redshift and provides database utilities
"""

import logging
from typing import Optional, List
import boto3
from botocore.exceptions import ClientError
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, pool
from app.config_aws import config_aws

logger = logging.getLogger(__name__)


class RedshiftDatabase:
    """Wrapper for Redshift database connection"""

    def __init__(self):
        self._db: Optional[SQLDatabase] = None
        self._redshift_client: Optional[boto3.client] = None
        self._connection_uri = None

    def _get_iam_credentials(self) -> dict:
        """
        Get temporary IAM credentials for Redshift

        Returns:
            dict: Temporary credentials
        """
        try:
            if self._redshift_client is None:
                self._redshift_client = boto3.client(
                    'redshift',
                    region_name=config_aws.AWS_REGION
                )

            response = self._redshift_client.get_cluster_credentials(
                DbUser=config_aws.REDSHIFT_USER,
                DbName=config_aws.REDSHIFT_DATABASE,
                ClusterIdentifier=config_aws.REDSHIFT_CLUSTER_IDENTIFIER,
                DurationSeconds=3600,  # 1 hour
                AutoCreate=False,
            )

            logger.info("Successfully obtained IAM credentials for Redshift")
            return {
                'user': response['DbUser'],
                'password': response['DbPassword'],
            }

        except ClientError as e:
            logger.error(f"Failed to get IAM credentials: {str(e)}")
            raise

    def _build_connection_uri(self) -> str:
        """
        Build connection URI with credentials

        Returns:
            str: SQLAlchemy connection URI
        """
        if config_aws.REDSHIFT_USE_IAM:
            credentials = self._get_iam_credentials()
            return (
                f"postgresql+psycopg2://{credentials['user']}:{credentials['password']}"
                f"@{config_aws.REDSHIFT_HOST}:{config_aws.REDSHIFT_PORT}/{config_aws.REDSHIFT_DATABASE}"
            )
        else:
            return config_aws.get_redshift_uri()

    def get_database(self) -> SQLDatabase:
        """
        Get or create SQLDatabase connection to Redshift

        Returns:
            SQLDatabase: LangChain SQLDatabase instance
        """
        if self._db is None:
            try:
                logger.info(f"Connecting to Redshift: {config_aws.REDSHIFT_DATABASE}")

                # Build connection URI (may include IAM credentials)
                self._connection_uri = self._build_connection_uri()

                # Create SQLAlchemy engine for Redshift
                # Using NullPool for serverless environments (Lambda, ECS)
                engine = create_engine(
                    self._connection_uri,
                    poolclass=pool.NullPool,
                    echo=False,
                    connect_args={
                        "sslmode": "require",  # Enforce SSL
                        "application_name": "automotive_chatbot",
                    }
                )

                # Create LangChain SQLDatabase
                self._db = SQLDatabase(
                    engine=engine,
                    schema=config_aws.REDSHIFT_SCHEMA,
                    sample_rows_in_table_info=3,
                    max_string_length=1000,
                )

                logger.info("Successfully connected to Redshift")

            except Exception as e:
                logger.error(f"Failed to connect to Redshift: {str(e)}")
                raise

        return self._db

    def get_redshift_client(self) -> boto3.client:
        """
        Get Redshift boto3 client for direct operations

        Returns:
            boto3.client: AWS Redshift client
        """
        if self._redshift_client is None:
            try:
                self._redshift_client = boto3.client(
                    'redshift',
                    region_name=config_aws.AWS_REGION
                )
                logger.info("Redshift client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redshift client: {str(e)}")
                raise

        return self._redshift_client

    def get_table_names(self) -> List[str]:
        """
        Get list of table names in the schema

        Returns:
            List[str]: List of table names
        """
        try:
            db = self.get_database()
            return db.get_usable_table_names()
        except Exception as e:
            logger.error(f"Failed to get table names: {str(e)}")
            return []

    def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
        """
        Get table schema information

        Args:
            table_names: Optional list of specific tables to get info for

        Returns:
            str: Table schema information
        """
        try:
            db = self.get_database()
            return db.get_table_info(table_names=table_names)
        except Exception as e:
            logger.error(f"Failed to get table info: {str(e)}")
            return f"Error retrieving table information: {str(e)}"

    def run_query(self, query: str) -> str:
        """
        Execute a SQL query directly

        Args:
            query: SQL query to execute

        Returns:
            str: Query results
        """
        try:
            db = self.get_database()
            result = db.run(query)
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return f"Error executing query: {str(e)}"

    def test_connection(self) -> dict:
        """
        Test database connection and return status

        Returns:
            dict: Connection status information
        """
        try:
            db = self.get_database()
            table_names = self.get_table_names()

            return {
                "status": "success",
                "database": config_aws.REDSHIFT_DATABASE,
                "schema": config_aws.REDSHIFT_SCHEMA,
                "tables": table_names,
                "table_count": len(table_names),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def close(self):
        """Close database connections"""
        if self._db is not None:
            try:
                # SQLDatabase doesn't have explicit close, but we can dispose the engine
                if hasattr(self._db, '_engine'):
                    self._db._engine.dispose()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {str(e)}")
            finally:
                self._db = None

        if self._redshift_client is not None:
            try:
                # Boto3 clients don't need explicit closing in most cases
                logger.info("Redshift client closed")
            except Exception as e:
                logger.warning(f"Error closing Redshift client: {str(e)}")
            finally:
                self._redshift_client = None


# Global database instance
_db_instance: Optional[RedshiftDatabase] = None


def get_database_instance() -> RedshiftDatabase:
    """
    Get singleton database instance

    Returns:
        RedshiftDatabase: Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = RedshiftDatabase()
    return _db_instance


def initialize_database() -> dict:
    """
    Initialize database connection and return status

    Returns:
        dict: Initialization status
    """
    try:
        db_instance = get_database_instance()
        return db_instance.test_connection()
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
