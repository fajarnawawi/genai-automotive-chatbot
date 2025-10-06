# Quick Reference Card - Automotive Sales Analytics Chatbot

## Essential Commands

### Local Development

```bash
# Setup
cd chatbot/cloud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your settings

# Run
streamlit run app/main.py

# Test
python test_setup.py
```

### Authentication

```bash
# Login
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### BigQuery Quick Checks

```bash
# List datasets
bq ls

# List tables
bq ls YOUR_PROJECT_ID:automotive_data

# Row counts
bq query --nouse_legacy_sql 'SELECT COUNT(*) FROM `PROJECT_ID.automotive_data.vehicles`'

# Test query
bq query --nouse_legacy_sql 'SELECT * FROM `PROJECT_ID.automotive_data.vehicles` LIMIT 5'
```

### Cloud Run - Quick Deploy

```bash
# Automated (recommended)
./deploy.sh

# Manual
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/chatbot-images/automotive-chatbot:latest

gcloud run deploy automotive-chatbot \
  --image us-central1-docker.pkg.dev/PROJECT_ID/chatbot-images/automotive-chatbot:latest \
  --region us-central1 \
  --memory 2Gi \
  --allow-unauthenticated \
  --env-vars-file env-vars.yaml
```

### Cloud Run - Management

```bash
# List services
gcloud run services list

# Get URL
gcloud run services describe SERVICE_NAME --region REGION --format='value(status.url)'

# View logs
gcloud run services logs tail SERVICE_NAME --region REGION

# Update env vars
gcloud run services update SERVICE_NAME --region REGION --set-env-vars KEY=VALUE

# Update resources
gcloud run services update SERVICE_NAME --region REGION --memory 4Gi --cpu 4

# Delete
gcloud run services delete SERVICE_NAME --region REGION
```

## Configuration Reference

### Environment Variables (.env)

```bash
# Required
GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=automotive_data
GEMINI_MODEL=gemini-1.5-pro

# Optional - Credentials (local only)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Optional - Tuning
GEMINI_TEMPERATURE=0.1              # 0-1, lower = more focused
GEMINI_MAX_OUTPUT_TOKENS=2048       # Max response length
SQL_AGENT_MAX_ITERATIONS=15         # Max agent steps
SQL_TOP_K_RESULTS=10                # Limit query results
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
```

### Cloud Run Service Account Roles

```bash
roles/bigquery.dataViewer       # Read BigQuery data
roles/bigquery.jobUser          # Run BigQuery queries  
roles/aiplatform.user           # Use Vertex AI
roles/run.invoker              # Invoke Cloud Run service
roles/logging.logWriter        # Write logs
```

## Common Query Patterns

### Sales Analysis
```
"What were our total sales in California last quarter?"
"Show me revenue by month for 2024"
"Which state had the highest sales?"
"What's the average sale price for SUVs?"
```

### Product Performance
```
"Top 5 best-selling vehicle models"
"Compare sedan sales to SUV sales"
"Which Toyota models sold the most?"
"Show me vehicles with sale price below MSRP"
```

### Dealership Insights
```
"Which dealership had the most sales?"
"List all dealerships in Texas"
"Show dealership revenue by state"
"Which dealerships sold Tesla vehicles?"
```

### Customer Analytics
```
"How many customers registered in Q3 2024?"
"Show customer registration trends"
"New customers per month in 2024"
```

### Marketing & Campaigns
```
"Total marketing budget in 2023"
"List campaigns in summer 2024"
"Which campaigns had the largest budgets?"
```

### Competitive Intelligence
```
"How do our sales compare to Tesla?"
"Competitor market share in California"
"Show Tesla sales trends"
```

## Troubleshooting Quick Checks

```bash
# Test all components
python test_setup.py

# Check imports
python -c "import streamlit; import google.cloud.bigquery; import vertexai; print('✅ All good')"

# Verify credentials
gcloud auth list
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test BigQuery
bq ls PROJECT_ID:automotive_data

# Check API enablement
gcloud services list --enabled | grep -E "(bigquery|aiplatform|run)"

# View app logs (Cloud Run)
gcloud run services logs read SERVICE_NAME --region REGION --limit 20
```

## File Structure

```
cloud/
├── app/
│   ├── config.py       # Configuration management
│   ├── database.py     # BigQuery connection
│   ├── llm.py          # Vertex AI Gemini
│   ├── agent.py        # LangChain SQL agent
│   └── main.py         # Streamlit app
├── requirements.txt    # Dependencies
├── Dockerfile          # Container build
├── .env.template       # Config template
├── env-vars.yaml       # Cloud Run env vars
├── deploy.sh           # Deploy script
└── test_setup.py       # Test suite
```

## Resource Recommendations

### Development
```bash
--memory=2Gi
--cpu=2
--min-instances=0
--max-instances=5
--timeout=300
```

### Production (Low Traffic)
```bash
--memory=2Gi
--cpu=2
--min-instances=1
--max-instances=10
--timeout=600
--concurrency=80
```

### Production (High Traffic)
```bash
--memory=4Gi
--cpu=4
--min-instances=2
--max-instances=20
--timeout=600
--concurrency=100
```

## Cost Estimates (Monthly)

### Development
- Cloud Run: $0-10
- Vertex AI: $10-20
- **Total: ~$10-30**

### Production (Low)
- Cloud Run: $40-60 (1 min instance)
- Vertex AI: $50-100 (1K queries/day)
- **Total: ~$90-160**

### Production (High)
- Cloud Run: $200-400 (multi-instance)
- Vertex AI: $200-500 (5K+ queries/day)
- **Total: ~$400-900**

## Support Resources

- 📖 **README.md** - Overview & quick start
- 🛠️ **LOCAL_DEVELOPMENT.md** - Local setup
- ☁️ **DEPLOYMENT_GUIDE.md** - Cloud deployment
- 🔍 **TROUBLESHOOTING.md** - Common issues
- 📊 **PROJECT_SUMMARY.md** - Complete details

## Key Links

```bash
# Cloud Console
https://console.cloud.google.com/run
https://console.cloud.google.com/bigquery
https://console.cloud.google.com/vertex-ai

# Documentation
https://cloud.google.com/run/docs
https://cloud.google.com/bigquery/docs
https://cloud.google.com/vertex-ai/docs
https://docs.streamlit.io
https://python.langchain.com
```

---

**Pro Tips:**
- Always test locally before deploying
- Use `--dry-run` flag when testing gcloud commands
- Keep `.env` file secure and never commit it
- Use minimum instances in production to avoid cold starts
- Monitor costs in Cloud Console billing
- Set up budget alerts to avoid surprises
- Enable Cloud Logging for debugging
- Use `deploy.sh` for consistent deployments

**Version**: 1.0  
**Last Updated**: October 2025
