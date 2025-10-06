"""
SQL Agent Module
Creates and manages LangChain SQL agent for natural language querying
"""

import logging
from typing import Optional, Dict, Any
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain.agents import AgentExecutor, AgentType  # Add AgentType
from langchain_core.messages import SystemMessage
from app.config import config
from app.database import get_database_instance
from app.llm import get_llm_instance

logger = logging.getLogger(__name__)


# System prompt for the SQL agent
SQL_AGENT_SYSTEM_PROMPT = """You are an expert automotive sales analyst with deep knowledge of SQL and BigQuery.
You help business users get insights from the automotive sales database by converting their natural language questions into SQL queries.

Database Schema:
The database contains 6 tables about automotive sales:
1. **vehicles** - Vehicle inventory (vehicle_id, make, model, year, body_type, msrp)
2. **dealerships** - Dealership locations (dealership_id, name, city, state)
3. **customers** - Customer information (customer_id, first_name, registration_date)
4. **sales_transactions** - Transaction records (transaction_id, vehicle_id, customer_id, dealership_id, sale_date, sale_price)
5. **marketing_campaigns** - Marketing campaign data (campaign_id, campaign_name, start_date, end_date, budget)
6. **competitor_sales** - Competitor sales data (record_id, competitor_make, sale_month, region, units_sold)

CRITICAL - BigQuery SQL Syntax:
- For year extraction: EXTRACT(YEAR FROM date_column) NOT strftime
- For month extraction: EXTRACT(MONTH FROM date_column)
- For date filtering: WHERE date_column >= '2024-01-01'
- Table names already qualified, use them as-is
- Use standard SQL syntax, NOT SQLite functions

Guidelines:
- Always start by understanding what tables contain the data needed
- Use table descriptions to understand the schema before writing queries
- For time-based queries, use EXTRACT() function for date parts
- When calculating metrics, use appropriate aggregations (SUM, AVG, COUNT)
- For top/bottom queries, use ORDER BY with LIMIT
- Join tables appropriately using foreign keys
- Return clean, formatted results
- If a query might return many rows, limit results to top {top_k}
- Always explain your reasoning before executing queries
- If you're unsure about the data, query the schema first

Data Notes:
- Date range: January 2023 - October 2024
- sale_price is the final transaction price (may be below MSRP due to discounts)
- All monetary values are in USD
- Use DATE format 'YYYY-MM-DD' for date comparisons

Be helpful, accurate, and provide insights along with the data!
"""


class SQLAgentManager:
    """Manager for SQL Agent operations"""
    
    def __init__(self):
        self._agent: Optional[AgentExecutor] = None
        self._toolkit: Optional[SQLDatabaseToolkit] = None
    
    def create_agent(self) -> AgentExecutor:
        """
        Create SQL agent compatible with Gemini 2.0
        
        Returns:
            AgentExecutor: Configured SQL agent
        """
        if self._agent is None:
            try:
                # Get database and LLM
                db_instance = get_database_instance()
                llm_manager = get_llm_instance()
                
                db = db_instance.get_database()
                llm = llm_manager.get_llm()
                
                logger.info("Creating SQL agent toolkit...")
                
                # Create SQL Database Toolkit
                self._toolkit = SQLDatabaseToolkit(
                    db=db,
                    llm=llm,
                )
                
                logger.info("Creating SQL agent with Gemini 2.0 compatibility...")
                
                # Use ZERO_SHOT_REACT_DESCRIPTION for Gemini 2.0 compatibility
                from langchain.agents import AgentType
                
                self._agent = create_sql_agent(
                    llm=llm,
                    toolkit=self._toolkit,
                    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=True,
                    max_iterations=config.SQL_AGENT_MAX_ITERATIONS,
                    max_execution_time=config.SQL_AGENT_MAX_EXECUTION_TIME,
                    handle_parsing_errors=True,
                    agent_executor_kwargs={
                        "return_intermediate_steps": True,
                    },
                    prefix=SQL_AGENT_SYSTEM_PROMPT.format(
                        top_k=config.SQL_TOP_K_RESULTS
                    ),
                )
                
                logger.info("SQL agent created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create SQL agent: {str(e)}")
                raise
        
        return self._agent
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a natural language query using the SQL agent
        
        Args:
            question: Natural language question
            
        Returns:
            dict: Query results with output and metadata
        """
        try:
            agent = self.create_agent()
            
            logger.info(f"Processing query: {question}")
            
            # Execute agent
            result = agent.invoke({"input": question})
            
            # Extract output
            output = result.get("output", "No response generated")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Extract SQL queries from intermediate steps
            sql_queries = []
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    if hasattr(action, 'tool') and 'sql' in action.tool.lower():
                        if hasattr(action, 'tool_input'):
                            sql_queries.append(action.tool_input)
            
            return {
                "status": "success",
                "question": question,
                "answer": output,
                "sql_queries": sql_queries,
                "steps_count": len(intermediate_steps),
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return {
                "status": "error",
                "question": question,
                "error": str(e),
            }
    
    def get_toolkit_info(self) -> Dict[str, Any]:
        """
        Get information about available tools
        
        Returns:
            dict: Toolkit information
        """
        try:
            if self._toolkit is None:
                self.create_agent()
            
            tools = self._toolkit.get_tools()
            
            return {
                "status": "success",
                "tool_count": len(tools),
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                    }
                    for tool in tools
                ],
            }
        except Exception as e:
            logger.error(f"Failed to get toolkit info: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
            }


# Global agent instance
_agent_instance: Optional[SQLAgentManager] = None


def get_agent_instance() -> SQLAgentManager:
    """
    Get singleton SQL agent manager instance
    
    Returns:
        SQLAgentManager: Agent manager instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SQLAgentManager()
    return _agent_instance


def query_database(question: str) -> Dict[str, Any]:
    """
    Convenience function to query database with natural language
    
    Args:
        question: Natural language question
        
    Returns:
        dict: Query results
    """
    agent_manager = get_agent_instance()
    return agent_manager.query(question)


def initialize_agent() -> dict:
    """
    Initialize SQL agent and return status
    
    Returns:
        dict: Initialization status
    """
    try:
        agent_manager = get_agent_instance()
        agent_manager.create_agent()
        toolkit_info = agent_manager.get_toolkit_info()
        
        return {
            "status": "success",
            "message": "SQL agent initialized successfully",
            "tools_available": toolkit_info.get("tool_count", 0),
        }
    except Exception as e:
        logger.error(f"Agent initialization failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
