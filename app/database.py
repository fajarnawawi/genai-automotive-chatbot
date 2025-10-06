"""
BigQuery Database Connection Module
Handles connection to Google Cloud BigQuery and provides database utilities
"""

import logging
from typing import Optional, List
from google.cloud import bigquery
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, pool
from app.config import config

logger = logging.getLogger(__name__)


class BigQueryDatabase:
    """Wrapper for BigQuery database connection"""
    
    def __init__(self):
        self._db: Optional[SQLDatabase] = None
        self._client: Optional[bigquery.Client] = None
        self._connection_uri = config.get_bigquery_uri()
    
    def get_database(self) -> SQLDatabase:
        """
        Get or create SQLDatabase connection to BigQuery
        
        Returns:
            SQLDatabase: LangChain SQLDatabase instance
        """
        if self._db is None:
            try:
                logger.info(f"Connecting to BigQuery: {config.BIGQUERY_DATASET}")
                
                # Create SQLAlchemy engine for BigQuery
                # Using NullPool to avoid connection pooling issues with BigQuery
                engine = create_engine(
                    self._connection_uri,
                    poolclass=pool.NullPool,
                    echo=False,
                )
                
                # Create LangChain SQLDatabase
                # Don't use schema parameter - it causes BigQuery session variable errors
                self._db = SQLDatabase(
                    engine=engine,
                    sample_rows_in_table_info=3,
                    max_string_length=1000,
                )
                
                logger.info("Successfully connected to BigQuery")
                
            except Exception as e:
                logger.error(f"Failed to connect to BigQuery: {str(e)}")
                raise
        
        return self._db
    
    def get_client(self) -> bigquery.Client:
        """
        Get BigQuery client for direct queries
        
        Returns:
            bigquery.Client: Google Cloud BigQuery client
        """
        if self._client is None:
            try:
                self._client = bigquery.Client(
                    project=config.PROJECT_ID,
                    location=config.BIGQUERY_LOCATION,
                )
                logger.info("BigQuery client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize BigQuery client: {str(e)}")
                raise
        
        return self._client
    
    def get_table_names(self) -> List[str]:
        """
        Get list of table names in the dataset
        
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
                "database": config.BIGQUERY_DATASET,
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
        
        if self._client is not None:
            try:
                self._client.close()
                logger.info("BigQuery client closed")
            except Exception as e:
                logger.warning(f"Error closing BigQuery client: {str(e)}")
            finally:
                self._client = None


# Global database instance
_db_instance: Optional[BigQueryDatabase] = None


def get_database_instance() -> BigQueryDatabase:
    """
    Get singleton database instance
    
    Returns:
        BigQueryDatabase: Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = BigQueryDatabase()
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
