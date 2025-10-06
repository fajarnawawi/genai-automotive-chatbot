"""
Automotive Sales Analytics Chatbot
Main Streamlit Application
"""

import streamlit as st
import logging
from datetime import datetime
from typing import List, Dict
import sys

# Add parent directory to path for module imports
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import config
from app.database import initialize_database, get_database_instance
from app.llm import initialize_llm
from app.agent import query_database, initialize_agent

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .status-success {
        color: #00cc00;
    }
    .status-error {
        color: #ff0000;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    
    if "db_status" not in st.session_state:
        st.session_state.db_status = None
    
    if "llm_status" not in st.session_state:
        st.session_state.llm_status = None
    
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = None


def initialize_system():
    """Initialize all system components"""
    if not st.session_state.initialized:
        with st.spinner("Initializing system..."):
            try:
                # Validate configuration
                config.validate()
                
                # Initialize database
                db_status = initialize_database()
                st.session_state.db_status = db_status
                
                if db_status["status"] != "success":
                    st.error(f"Database initialization failed: {db_status.get('error', 'Unknown error')}")
                    return False
                
                # Initialize LLM
                llm_status = initialize_llm()
                st.session_state.llm_status = llm_status
                
                if llm_status["status"] != "success":
                    st.error(f"LLM initialization failed: {llm_status.get('error', 'Unknown error')}")
                    return False
                
                # Initialize agent
                agent_status = initialize_agent()
                st.session_state.agent_status = agent_status
                
                if agent_status["status"] != "success":
                    st.error(f"Agent initialization failed: {agent_status.get('error', 'Unknown error')}")
                    return False
                
                st.session_state.initialized = True
                logger.info("System initialized successfully")
                return True
                
            except Exception as e:
                st.error(f"System initialization error: {str(e)}")
                logger.error(f"System initialization failed: {str(e)}")
                return False
    
    return True


def display_sidebar():
    """Display sidebar with system information and controls"""
    with st.sidebar:
        st.title(f"{config.APP_ICON} Automotive Analytics")
        
        st.markdown("---")
        
        # System Status
        st.subheader("System Status")
        
        if st.session_state.initialized:
            st.success("✅ System Ready")
            
            # Database status
            if st.session_state.db_status:
                st.info(f"📊 Database: {st.session_state.db_status.get('table_count', 0)} tables")
            
            # LLM status
            if st.session_state.llm_status:
                st.info(f"🤖 Model: {config.GEMINI_MODEL}")
        else:
            st.warning("⏳ Initializing...")
        
        st.markdown("---")
        
        # Configuration
        st.subheader("Configuration")
        config_display = config.display_config()
        for key, value in config_display.items():
            st.text(f"{key}: {value}")
        
        st.markdown("---")
        
        # Sample Questions
        st.subheader("💡 Sample Questions")
        sample_questions = [
            "What were total sales in California last quarter?",
            "Which vehicle model sold the most in 2024?",
            "Show me the top 5 dealerships by revenue",
            "What's the average sale price by body type?",
            "How many marketing campaigns ran in Q3 2023?",
            "Compare our sales to Tesla in California",
        ]
        
        for i, question in enumerate(sample_questions, 1):
            if st.button(f"{i}. {question[:40]}...", key=f"sample_{i}", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        st.markdown("---")
        
        # Clear Chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.caption(f"Version 1.0 | Built with Streamlit & Gemini")


def display_welcome_message():
    """Display welcome message when chat is empty"""
    st.markdown(f"""
    ## Welcome to {config.APP_TITLE}! {config.APP_ICON}
    
    I'm your AI-powered automotive sales analyst. I can help you get insights from your sales data using natural language.
    
    ### What I can do:
    - 📊 **Sales Analysis**: Revenue, units sold, trends over time
    - 🚗 **Product Performance**: Best-selling models, body types, brands
    - 🏪 **Dealership Insights**: Performance by location, state, region
    - 👥 **Customer Analytics**: Registration trends, demographics
    - 💰 **Marketing ROI**: Campaign performance, budget analysis
    - 🎯 **Competitive Intelligence**: Market share, competitor analysis
    
    ### How to use:
    1. Type your question in natural language
    2. I'll convert it to SQL and query the database
    3. Get instant insights with explanations
    
    **Try asking a question from the sidebar, or type your own!**
    """)
    
    # Display database schema
    with st.expander("📚 View Database Schema"):
        try:
            db_instance = get_database_instance()
            tables = db_instance.get_table_names()
            
            st.write("**Available Tables:**")
            for table in tables:
                st.write(f"- `{table}`")
            
            st.markdown("---")
            st.write("**Detailed Schema:**")
            schema_info = db_instance.get_table_info()
            st.code(schema_info, language="sql")
            
        except Exception as e:
            st.error(f"Could not load schema: {str(e)}")


def process_user_query(question: str):
    """Process user query and display results"""
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "timestamp": datetime.now()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(question)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question and querying database..."):
            try:
                result = query_database(question)
                
                if result["status"] == "success":
                    # Display answer
                    st.write(result["answer"])
                    
                    # Display SQL queries in expander
                    if result.get("sql_queries"):
                        with st.expander("🔍 View SQL Queries"):
                            for i, query in enumerate(result["sql_queries"], 1):
                                st.code(query, language="sql")
                    
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "timestamp": datetime.now(),
                        "sql_queries": result.get("sql_queries", []),
                        "steps_count": result.get("steps_count", 0)
                    })
                    
                else:
                    error_msg = f"I encountered an error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now(),
                        "error": True
                    })
                
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                st.error(error_msg)
                logger.error(f"Query processing error: {str(e)}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now(),
                    "error": True
                })


def display_chat_history():
    """Display chat message history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display SQL queries for assistant messages
            if message["role"] == "assistant" and "sql_queries" in message:
                if message["sql_queries"]:
                    with st.expander("🔍 View SQL Queries"):
                        for i, query in enumerate(message["sql_queries"], 1):
                            st.code(query, language="sql")


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Initialize system
    if not initialize_system():
        st.stop()
    
    # Main title
    st.title(f"{config.APP_ICON} {config.APP_TITLE}")
    
    # Display welcome message or chat history
    if not st.session_state.messages:
        display_welcome_message()
    else:
        display_chat_history()
    
    # Chat input
    if question := st.chat_input("Ask a question about your automotive sales data..."):
        process_user_query(question)
        st.rerun()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")
