"""
Automotive Sales Analytics Chatbot - AWS Version
Main Streamlit Application with CloudWatch Integration
"""

import streamlit as st
import logging
import boto3
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config_aws import config_aws
from app.database_aws import initialize_database, get_database_instance
from app.llm_aws import initialize_llm
from app.agent_aws import query_database, initialize_agent

# Configure logging with CloudWatch support
def setup_logging():
    """Setup logging with optional CloudWatch integration"""
    # Basic logging configuration
    logging.basicConfig(
        level=getattr(logging, config_aws.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Optional: Add CloudWatch handler if running in AWS
    try:
        # Check if we're running in AWS environment (ECS, Lambda, EC2)
        if os.getenv('AWS_EXECUTION_ENV') or os.getenv('ECS_CONTAINER_METADATA_URI'):
            import watchtower

            cloudwatch_handler = watchtower.CloudWatchLogHandler(
                log_group=config_aws.CLOUDWATCH_LOG_GROUP,
                stream_name=config_aws.CLOUDWATCH_LOG_STREAM,
                use_queues=True,
                send_interval=60,
                create_log_group=True,
            )

            logger = logging.getLogger()
            logger.addHandler(cloudwatch_handler)
            logger.info("CloudWatch logging enabled")
    except Exception as e:
        logging.warning(f"CloudWatch logging not available: {str(e)}")

setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=config_aws.APP_TITLE,
    page_icon=config_aws.APP_ICON,
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
    .aws-badge {
        background: linear-gradient(90deg, #FF9900 0%, #FF6600 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
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
        with st.spinner("Initializing AWS services..."):
            try:
                # Validate configuration
                config_aws.validate()

                # Initialize database (Redshift)
                db_status = initialize_database()
                st.session_state.db_status = db_status

                if db_status["status"] != "success":
                    st.error(f"Redshift initialization failed: {db_status.get('error', 'Unknown error')}")
                    return False

                # Initialize LLM (Bedrock)
                llm_status = initialize_llm()
                st.session_state.llm_status = llm_status

                if llm_status["status"] != "success":
                    st.error(f"Bedrock initialization failed: {llm_status.get('error', 'Unknown error')}")
                    return False

                # Initialize agent
                agent_status = initialize_agent()
                st.session_state.agent_status = agent_status

                if agent_status["status"] != "success":
                    st.error(f"Agent initialization failed: {agent_status.get('error', 'Unknown error')}")
                    return False

                st.session_state.initialized = True
                logger.info("System initialized successfully on AWS")
                return True

            except Exception as e:
                st.error(f"System initialization error: {str(e)}")
                logger.error(f"System initialization failed: {str(e)}")
                return False

    return True


def display_sidebar():
    """Display sidebar with system information and controls"""
    with st.sidebar:
        st.title(f"{config_aws.APP_ICON} Automotive Analytics")
        st.markdown('<span class="aws-badge">AWS Edition</span>', unsafe_allow_html=True)

        st.markdown("---")

        # System Status
        st.subheader("System Status")

        if st.session_state.initialized:
            st.success("✅ System Ready")

            # Database status
            if st.session_state.db_status:
                st.info(f"📊 Redshift: {st.session_state.db_status.get('table_count', 0)} tables")

            # LLM status
            if st.session_state.llm_status:
                model_name = config_aws.BEDROCK_MODEL_ID.split('.')[-1].split('-')[0].title()
                st.info(f"🤖 Bedrock: {model_name}")
        else:
            st.warning("⏳ Initializing AWS services...")

        st.markdown("---")

        # Configuration
        st.subheader("Configuration")
        config_display = config_aws.display_config()
        for key, value in config_display.items():
            # Truncate long values
            display_value = str(value)
            if len(display_value) > 40:
                display_value = display_value[:37] + "..."
            st.text(f"{key}: {display_value}")

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
        st.caption(f"Version 1.0 AWS | Built with Streamlit, Bedrock & Redshift")


def display_welcome_message():
    """Display welcome message when chat is empty"""
    st.markdown(f"""
    ## Welcome to {config_aws.APP_TITLE}! {config_aws.APP_ICON}

    <span class="aws-badge">Powered by AWS Bedrock & Redshift</span>

    I'm your AI-powered automotive sales analyst running on AWS infrastructure. I can help you get insights from your sales data using natural language.

    ### What I can do:
    - 📊 **Sales Analysis**: Revenue, units sold, trends over time
    - 🚗 **Product Performance**: Best-selling models, body types, brands
    - 🏪 **Dealership Insights**: Performance by location, state, region
    - 👥 **Customer Analytics**: Registration trends, demographics
    - 💰 **Marketing ROI**: Campaign performance, budget analysis
    - 🎯 **Competitive Intelligence**: Market share, competitor analysis

    ### AWS Services Used:
    - **Amazon Bedrock**: Claude AI for natural language understanding
    - **Amazon Redshift**: High-performance data warehouse
    - **AWS IAM**: Secure authentication and authorization
    - **Amazon CloudWatch**: Application monitoring and logging

    ### How to use:
    1. Type your question in natural language
    2. I'll convert it to SQL and query Redshift
    3. Get instant insights with explanations

    **Try asking a question from the sidebar, or type your own!**
    """, unsafe_allow_html=True)

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
        with st.spinner("Analyzing with Claude and querying Redshift..."):
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
    st.title(f"{config_aws.APP_ICON} {config_aws.APP_TITLE}")

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
