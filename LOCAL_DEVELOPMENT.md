# Local Development Guide

## Prerequisites

- Python 3.11 or higher
- Google Cloud SDK (`gcloud` CLI)
- Access to Google Cloud Project with:
  - BigQuery with `automotive_data` dataset
  - Vertex AI API enabled
  - Service account with appropriate permissions

## Step 1: Clone and Setup

```bash
# Navigate to the project directory
cd /path/to/chatbot/cloud

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

Required variables to update in `.env`:
```bash
GCP_PROJECT_ID=your-actual-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

## Step 3: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Authenticate application default credentials
gcloud auth application-default login
```

## Step 4: Verify BigQuery Access

Test your BigQuery connection:

```bash
# List datasets
bq ls

# Query the automotive_data dataset
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `YOUR_PROJECT_ID.automotive_data.vehicles`'
```

Expected output: Should return 50

## Step 5: Run the Application Locally

```bash
# Run Streamlit application (make sure you're in cloud/ directory)
streamlit run app/main.py

# Or specify port
streamlit run app/main.py --server.port 8501

# Important: Always run from /path/to/chatbot/cloud/ directory
# NOT from /path/to/chatbot/cloud/app/
```

The application will open in your browser at `http://localhost:8501`

## Step 6: Test the Application

1. **Check System Status**
   - Look at the sidebar for system initialization status
   - Should show "✅ System Ready" when fully initialized

2. **Test with Sample Questions**
   - Click one of the sample questions in the sidebar
   - Or type your own question

3. **Verify SQL Generation**
   - Expand "View SQL Queries" to see generated SQL
   - Check that queries are valid and returning results

## Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```bash
# Ensure you're in the virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Authentication failed"
**Solution:**
```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Re-authenticate
gcloud auth application-default login

# Verify service account has correct permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SERVICE_ACCOUNT"
```

### Issue: "Cannot connect to BigQuery"
**Solution:**
```bash
# Verify BigQuery API is enabled
gcloud services enable bigquery.googleapis.com

# Check dataset exists
bq ls YOUR_PROJECT_ID:

# Test direct query
bq query --use_legacy_sql=false \
  'SELECT table_name FROM `YOUR_PROJECT_ID.automotive_data.INFORMATION_SCHEMA.TABLES`'
```

### Issue: "Vertex AI initialization failed"
**Solution:**
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verify location is correct
# us-central1, us-west1, europe-west1, etc.

# Check service account has Vertex AI User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

### Issue: Streamlit shows blank page
**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart the application
# Press Ctrl+C and run again
streamlit run app/main.py
```

## Development Tips

### Enable Debug Logging

Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

### Enable LangChain Tracing

For debugging LangChain execution:

1. Sign up for LangSmith (optional): https://smith.langchain.com/
2. Get API key
3. Update `.env`:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=automotive-chatbot
```

### Hot Reloading

Streamlit automatically reloads when you save changes to `.py` files. If it doesn't:
- Click "Always rerun" in the Streamlit interface
- Or press 'R' to manually rerun

### Testing Individual Components

```python
# Test database connection
python -c "from app.database import initialize_database; print(initialize_database())"

# Test LLM
python -c "from app.llm import initialize_llm; print(initialize_llm())"

# Test agent
python -c "from app.agent import initialize_agent; print(initialize_agent())"
```

## Code Structure

```
cloud/
├── app/
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration management
│   ├── database.py        # BigQuery connection
│   ├── llm.py             # Vertex AI Gemini integration
│   ├── agent.py           # LangChain SQL agent
│   └── main.py            # Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition
├── .env.template          # Environment variables template
├── .env                   # Your local environment (gitignored)
└── README.md              # Documentation
```

## Next Steps

Once local development is working:
1. Review the [Cloud Run Deployment Guide](DEPLOYMENT_GUIDE.md)
2. Build and test Docker container locally
3. Deploy to Cloud Run

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
