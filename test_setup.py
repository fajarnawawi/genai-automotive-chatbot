"""
Test Suite for Automotive Sales Analytics Chatbot
Run this script to validate all components before deployment
"""

import sys
import os
import logging
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Test results
test_results: List[Tuple[str, bool, str]] = []


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def print_result(test_name: str, passed: bool, message: str = ""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"    {message}")
    test_results.append((test_name, passed, message))


def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Module Imports")
    
    try:
        import streamlit
        print_result("Streamlit import", True, f"Version {streamlit.__version__}")
    except Exception as e:
        print_result("Streamlit import", False, str(e))
    
    try:
        import google.cloud.bigquery
        print_result("BigQuery import", True)
    except Exception as e:
        print_result("BigQuery import", False, str(e))
    
    try:
        import vertexai
        print_result("Vertex AI import", True)
    except Exception as e:
        print_result("Vertex AI import", False, str(e))
    
    try:
        import langchain
        print_result("LangChain import", True, f"Version {langchain.__version__}")
    except Exception as e:
        print_result("LangChain import", False, str(e))
    
    try:
        from langchain_google_vertexai import ChatVertexAI
        print_result("LangChain Vertex AI import", True)
    except Exception as e:
        print_result("LangChain Vertex AI import", False, str(e))
    
    try:
        from langchain_community.utilities import SQLDatabase
        print_result("LangChain SQL utilities import", True)
    except Exception as e:
        print_result("LangChain SQL utilities import", False, str(e))


def test_configuration():
    """Test configuration loading"""
    print_header("Testing Configuration")
    
    try:
        from app.config import config
        print_result("Configuration import", True)
        
        # Check required fields
        required_fields = ['PROJECT_ID', 'BIGQUERY_DATASET', 'GEMINI_MODEL']
        all_set = True
        for field in required_fields:
            value = getattr(config, field, None)
            if not value or value.startswith('YOUR_'):
                all_set = False
                print_result(f"Config: {field}", False, "Not configured")
            else:
                print_result(f"Config: {field}", True, f"Set to: {value}")
        
        if all_set:
            print_result("All required config fields", True)
        else:
            print_result("All required config fields", False, "Some fields not configured")
            
    except Exception as e:
        print_result("Configuration test", False, str(e))


def test_database_module():
    """Test database module"""
    print_header("Testing Database Module")
    
    try:
        from app.database import BigQueryDatabase, get_database_instance
        print_result("Database module import", True)
        
        # Try to get instance (won't connect without credentials)
        try:
            db_instance = get_database_instance()
            print_result("Database instance creation", True)
        except Exception as e:
            print_result("Database instance creation", False, str(e))
            
    except Exception as e:
        print_result("Database module test", False, str(e))


def test_llm_module():
    """Test LLM module"""
    print_header("Testing LLM Module")
    
    try:
        from app.llm import LLMManager, get_llm_instance
        print_result("LLM module import", True)
        
        try:
            llm_manager = get_llm_instance()
            print_result("LLM manager creation", True)
        except Exception as e:
            print_result("LLM manager creation", False, str(e))
            
    except Exception as e:
        print_result("LLM module test", False, str(e))


def test_agent_module():
    """Test agent module"""
    print_header("Testing Agent Module")
    
    try:
        from app.agent import SQLAgentManager, get_agent_instance
        print_result("Agent module import", True)
        
        try:
            agent_manager = get_agent_instance()
            print_result("Agent manager creation", True)
        except Exception as e:
            print_result("Agent manager creation", False, str(e))
            
    except Exception as e:
        print_result("Agent module test", False, str(e))


def test_main_application():
    """Test main application module"""
    print_header("Testing Main Application")
    
    try:
        # Import without running
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "app/main.py")
        if spec and spec.loader:
            print_result("Main application module loadable", True)
        else:
            print_result("Main application module loadable", False)
    except Exception as e:
        print_result("Main application test", False, str(e))


def test_environment():
    """Test environment setup"""
    print_header("Testing Environment")
    
    # Check Python version
    import sys
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_result("Python version", True, f"{version.major}.{version.minor}.{version.micro}")
    else:
        print_result("Python version", False, f"Need 3.11+, got {version.major}.{version.minor}")
    
    # Check environment variables
    env_vars = [
        'GCP_PROJECT_ID',
        'BIGQUERY_DATASET',
        'GEMINI_MODEL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print_result(f"Environment: {var}", True, f"Set")
        else:
            print_result(f"Environment: {var}", False, "Not set")
    
    # Check credentials
    creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds:
        if os.path.exists(creds):
            print_result("Google credentials file", True, f"Found at {creds}")
        else:
            print_result("Google credentials file", False, f"Path set but file not found: {creds}")
    else:
        print_result("Google credentials", False, "GOOGLE_APPLICATION_CREDENTIALS not set")


def test_docker_setup():
    """Test Docker configuration"""
    print_header("Testing Docker Configuration")
    
    # Check Dockerfile exists
    if os.path.exists('Dockerfile'):
        print_result("Dockerfile exists", True)
        
        # Check Dockerfile contents
        with open('Dockerfile', 'r') as f:
            content = f.read()
            if 'FROM python:3.11' in content:
                print_result("Dockerfile base image", True, "Python 3.11")
            else:
                print_result("Dockerfile base image", False, "Wrong Python version")
    else:
        print_result("Dockerfile exists", False)
    
    # Check .dockerignore exists
    if os.path.exists('.dockerignore'):
        print_result(".dockerignore exists", True)
    else:
        print_result(".dockerignore exists", False)
    
    # Check requirements.txt exists
    if os.path.exists('requirements.txt'):
        print_result("requirements.txt exists", True)
        
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
            print_result("Dependencies count", True, f"{len(lines)} packages")
    else:
        print_result("requirements.txt exists", False)


def test_documentation():
    """Test documentation completeness"""
    print_header("Testing Documentation")
    
    docs = [
        'README.md',
        'LOCAL_DEVELOPMENT.md',
        'DEPLOYMENT_GUIDE.md',
        'PROJECT_SUMMARY.md',
        '.env.template',
        'env-vars.yaml'
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            print_result(f"Documentation: {doc}", True, f"{size} bytes")
        else:
            print_result(f"Documentation: {doc}", False, "Not found")


def test_deployment_script():
    """Test deployment script"""
    print_header("Testing Deployment Script")
    
    if os.path.exists('deploy.sh'):
        print_result("deploy.sh exists", True)
        
        # Check if executable
        import stat
        st = os.stat('deploy.sh')
        if st.st_mode & stat.S_IXUSR:
            print_result("deploy.sh is executable", True)
        else:
            print_result("deploy.sh is executable", False, "Run: chmod +x deploy.sh")
    else:
        print_result("deploy.sh exists", False)


def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(test_results)
    passed = sum(1 for _, p, _ in test_results if p)
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {(passed/total*100):.1f}%\n")
    
    if failed > 0:
        print("\nFailed tests:")
        for name, passed, message in test_results:
            if not passed:
                print(f"  ❌ {name}")
                if message:
                    print(f"     {message}")
    
    print("\n" + "="*60)
    if failed == 0:
        print("🎉 All tests passed! Ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please fix before deployment.")
    print("="*60 + "\n")
    
    return failed == 0


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Automotive Sales Analytics Chatbot - Test Suite")
    print("="*60)
    
    # Run all tests
    test_imports()
    test_configuration()
    test_environment()
    test_database_module()
    test_llm_module()
    test_agent_module()
    test_main_application()
    test_docker_setup()
    test_documentation()
    test_deployment_script()
    
    # Print summary
    all_passed = print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
