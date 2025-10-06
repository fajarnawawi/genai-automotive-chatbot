# Troubleshooting Guide

## Quick Diagnostics

### Run Test Suite

```bash
cd chatbot/cloud
python test_setup.py
```

This will check:
- All required dependencies
- Configuration settings
- Environment variables
- Module imports
- Docker setup
- Documentation

---

## Common Issues and Solutions

### 1. Installation Issues

#### Issue: `pip install` fails with dependency conflicts

**Symptoms:**
```
ERROR: Cannot install X because these package versions have conflicting dependencies
```

**Solution:**
```bash
# Create fresh virtual environment
python -m venv venv --clear
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install from scratch
pip install -r requirements.txt
```

#### Issue: `ModuleNotFoundError` for installed packages

**Symptoms:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
# Verify you're in virtual environment
which python  # Should show venv path

# If not, activate it
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

---

### 2. Authentication Issues

#### Issue: "Could not automatically determine credentials"

**Symptoms:**
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Solution:**
```bash
# Option 1: Application default credentials (recommended for local dev)
gcloud auth application-default login

# Option 2: Set service account key path
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 3: Login to gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Issue: "Permission denied" when accessing BigQuery

**Symptoms:**
```
403 Permission denied: BigQuery BigQuery: Permission denied while getting Drive credentials
```

**Solution:**
```bash
# Check current account
gcloud auth list

# Verify service account has correct roles
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_SERVICE_ACCOUNT"

# Add required roles if missing
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/bigquery.jobUser"
```

---

### 3. Configuration Issues

#### Issue: "Missing required configuration"

**Symptoms:**
```
ValueError: Missing required configuration: PROJECT_ID
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# If not, create from template
cp .env.template .env

# Edit with your values
nano .env
# Update: GCP_PROJECT_ID=your-actual-project-id

# Load environment variables
export $(cat .env | xargs)

# Verify
echo $GCP_PROJECT_ID
```

#### Issue: Configuration not loading

**Symptoms:**
- App shows "YOUR_PROJECT_ID" or placeholder values
- Environment variables not recognized

**Solution:**
```bash
# Method 1: Export variables manually
export GCP_PROJECT_ID="your-project-id"
export BIGQUERY_DATASET="automotive_data"

# Method 2: Load from .env file
python -c "from dotenv import load_dotenv; load_dotenv()"

# Method 3: Set in shell profile
echo 'export GCP_PROJECT_ID="your-project-id"' >> ~/.bashrc
source ~/.bashrc
```

---

### 4. BigQuery Connection Issues

#### Issue: "Cannot connect to BigQuery"

**Symptoms:**
```
sqlalchemy.exc.DatabaseError: Could not connect to BigQuery
```

**Solution:**
```bash
# 1. Verify BigQuery API is enabled
gcloud services enable bigquery.googleapis.com --project=YOUR_PROJECT_ID

# 2. Test connection directly
bq ls YOUR_PROJECT_ID:

# 3. Check dataset exists
bq ls YOUR_PROJECT_ID:automotive_data

# 4. Test query
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM `YOUR_PROJECT_ID.automotive_data.vehicles`'

# If dataset doesn't exist, upload data first
# See data engineer's BIGQUERY_UPLOAD_GUIDE.md
```

#### Issue: "Table not found"

**Symptoms:**
```
google.api_core.exceptions.NotFound: Table not found
```

**Solution:**
```bash
# List all tables
bq ls YOUR_PROJECT_ID:automotive_data

# Expected tables:
# - vehicles (50 rows)
# - dealerships (40 rows)
# - customers (80 rows)
# - sales_transactions (120 rows)
# - marketing_campaigns (30 rows)
# - competitor_sales (160 rows)

# If missing, upload data from data engineer deliverables
```

---

### 5. Vertex AI / Gemini Issues

#### Issue: "Vertex AI API not enabled"

**Symptoms:**
```
google.api_core.exceptions.PermissionDenied: Vertex AI API has not been used
```

**Solution:**
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID

# Wait 1-2 minutes for propagation
sleep 120

# Verify
gcloud services list --enabled | grep aiplatform
```

#### Issue: "Invalid model name"

**Symptoms:**
```
ValueError: Invalid model name: gemini-1.5-pro
```

**Solution:**
```bash
# Check available models in your region
gcloud ai models list --region=us-central1

# Update .env with correct model name
# Valid options:
# - gemini-1.5-pro
# - gemini-1.5-flash
# - gemini-1.0-pro

# If model not available in region, change region
export GCP_LOCATION="us-central1"  # or us-east1, europe-west1
```

#### Issue: "Quota exceeded"

**Symptoms:**
```
429 Quota exceeded for quota metric 'GenerateContent requests per minute'
```

**Solution:**
```bash
# Request quota increase in Cloud Console:
# 1. Go to: https://console.cloud.google.com/iam-admin/quotas
# 2. Filter: "Vertex AI API"
# 3. Select quota: "GenerateContent requests per minute per region"
# 4. Click "Edit Quotas" and request increase

# Temporary workaround: Add retry logic or rate limiting
# Already implemented in the agent with max_execution_time
```

---

### 6. Streamlit Issues

#### Issue: Streamlit won't start

**Symptoms:**
```
streamlit: command not found
```

**Solution:**
```bash
# Ensure streamlit is installed
pip install streamlit

# If in virtual environment, activate first
source venv/bin/activate

# Try running with python -m
python -m streamlit run app/main.py
```

#### Issue: "Address already in use"

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run app/main.py --server.port 8502
```

#### Issue: Blank page or loading forever

**Symptoms:**
- Browser shows blank page
- Stuck on "Please wait..."

**Solution:**
```bash
# 1. Clear Streamlit cache
streamlit cache clear

# 2. Restart with fresh session
# Press Ctrl+C and restart
streamlit run app/main.py

# 3. Check browser console for errors (F12)

# 4. Try different browser

# 5. Check logs
# Look for errors in terminal output
```

---

### 7. Docker Issues

#### Issue: Docker build fails

**Symptoms:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete
```

**Solution:**
```bash
# 1. Increase Docker memory (Docker Desktop → Settings → Resources)

# 2. Build with more verbose output
docker build -t test . --progress=plain

# 3. Build without cache
docker build -t test . --no-cache

# 4. Check requirements.txt for issues
cat requirements.txt

# 5. Test requirements installation locally first
pip install -r requirements.txt
```

#### Issue: Container starts but app not accessible

**Symptoms:**
```
docker ps shows container running but http://localhost:8080 doesn't work
```

**Solution:**
```bash
# 1. Check container logs
docker logs CONTAINER_ID

# 2. Verify port mapping
docker ps
# Should show: 0.0.0.0:8080->8080/tcp

# 3. Try accessing directly
docker exec -it CONTAINER_ID curl http://localhost:8080/_stcore/health

# 4. Check if port is actually exposed
docker inspect CONTAINER_ID | grep -A 10 ExposedPorts
```

---

### 8. Cloud Run Deployment Issues

#### Issue: Build timeout

**Symptoms:**
```
ERROR: build step 0 "gcr.io/cloud-builders/docker" failed: step exited with non-zero status: 1
```

**Solution:**
```bash
# Increase timeout
gcloud builds submit --timeout=30m --tag=IMAGE_URI

# Or in cloudbuild.yaml
timeout: 1800s
```

#### Issue: Service fails to start

**Symptoms:**
```
Revision failed with message: The user-provided container failed to start and listen on the port defined by PORT
```

**Solution:**
```bash
# 1. Check Cloud Run logs
gcloud run services logs read SERVICE_NAME --region=REGION --limit=100

# 2. Verify Dockerfile exposes correct port (8080)
grep EXPOSE Dockerfile

# 3. Test container locally first
docker run -p 8080:8080 -e GCP_PROJECT_ID=test IMAGE_URI

# 4. Check environment variables are set
gcloud run services describe SERVICE_NAME --region=REGION --format=json | jq '.spec.template.spec.containers[0].env'
```

#### Issue: "Permission denied" in Cloud Run

**Symptoms:**
```
Permission denied while getting BigQuery dataset
```

**Solution:**
```bash
# Verify service account
SERVICE_ACCOUNT=$(gcloud run services describe SERVICE_NAME \
  --region=REGION --format='value(spec.template.spec.serviceAccountName)')

echo "Using service account: $SERVICE_ACCOUNT"

# Grant required permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

---

### 9. Query/Agent Issues

#### Issue: Agent returns "No answer"

**Symptoms:**
```
Agent Output: I don't have enough information to answer this question
```

**Solution:**
1. **Check if question is too vague:**
   - ❌ Bad: "Show me data"
   - ✅ Good: "Show me total sales by state in 2024"

2. **Verify data exists:**
```sql
-- Check data range
SELECT MIN(sale_date), MAX(sale_date) 
FROM `PROJECT_ID.automotive_data.sales_transactions`
```

3. **Try simpler question first:**
   - Start with: "How many vehicles are in the database?"
   - Then build up to complex queries

#### Issue: SQL errors in agent output

**Symptoms:**
```
Error executing query: Syntax error: Expected end of input but got identifier
```

**Solution:**
1. **Check table names in logs**
2. **Verify schema:**
```bash
bq show --schema PROJECT_ID:automotive_data.vehicles
```

3. **Increase agent iterations:**
```python
# In .env
SQL_AGENT_MAX_ITERATIONS=20
```

4. **Enable verbose logging:**
```python
# In .env
LOG_LEVEL=DEBUG
```

---

### 10. Performance Issues

#### Issue: Slow response times

**Symptoms:**
- Queries take >30 seconds
- Frequent timeouts

**Solution:**
```bash
# 1. Increase Cloud Run resources
gcloud run services update SERVICE_NAME \
  --region=REGION \
  --memory=4Gi \
  --cpu=4

# 2. Increase timeout
gcloud run services update SERVICE_NAME \
  --region=REGION \
  --timeout=600

# 3. Use minimum instances to avoid cold starts
gcloud run services update SERVICE_NAME \
  --region=REGION \
  --min-instances=1

# 4. Optimize queries (limit results)
export SQL_TOP_K_RESULTS=5
```

#### Issue: High memory usage

**Symptoms:**
```
Container memory exceeded
```

**Solution:**
```bash
# Increase memory allocation
gcloud run services update SERVICE_NAME \
  --region=REGION \
  --memory=4Gi

# Or adjust in deployment
--memory=8Gi
```

---

## Diagnostic Commands

### Check System Status

```bash
# Run all tests
python test_setup.py

# Check Python version
python --version

# Check pip packages
pip list

# Check environment variables
env | grep GCP
env | grep BIGQUERY
env | grep GEMINI
```

### Check Google Cloud Status

```bash
# Current project
gcloud config get-value project

# Current account
gcloud auth list

# Enabled APIs
gcloud services list --enabled | grep -E "(bigquery|aiplatform|run|cloudbuild)"

# Service account permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_SERVICE_ACCOUNT"
```

### Check BigQuery

```bash
# List datasets
bq ls PROJECT_ID:

# List tables in dataset
bq ls PROJECT_ID:automotive_data

# Row counts
bq query --use_legacy_sql=false '
SELECT 
  "vehicles" as table_name, COUNT(*) as rows FROM `PROJECT_ID.automotive_data.vehicles`
UNION ALL
SELECT "dealerships", COUNT(*) FROM `PROJECT_ID.automotive_data.dealerships`
UNION ALL
SELECT "customers", COUNT(*) FROM `PROJECT_ID.automotive_data.customers`
UNION ALL
SELECT "sales_transactions", COUNT(*) FROM `PROJECT_ID.automotive_data.sales_transactions`
UNION ALL
SELECT "marketing_campaigns", COUNT(*) FROM `PROJECT_ID.automotive_data.marketing_campaigns`
UNION ALL
SELECT "competitor_sales", COUNT(*) FROM `PROJECT_ID.automotive_data.competitor_sales`
'
```

### Check Cloud Run

```bash
# List services
gcloud run services list

# Service details
gcloud run services describe SERVICE_NAME --region=REGION

# Recent logs
gcloud run services logs read SERVICE_NAME --region=REGION --limit=50

# Stream logs
gcloud run services logs tail SERVICE_NAME --region=REGION
```

---

## Getting Help

### Where to Look

1. **Documentation in this repo:**
   - README.md - Overview and quick start
   - LOCAL_DEVELOPMENT.md - Local setup
   - DEPLOYMENT_GUIDE.md - Cloud deployment
   - PROJECT_SUMMARY.md - Complete project details

2. **Logs:**
   ```bash
   # Local logs: Check terminal output
   
   # Cloud Run logs
   gcloud run services logs read SERVICE_NAME --region=REGION
   
   # Cloud Console
   # https://console.cloud.google.com/run
   ```

3. **Test output:**
   ```bash
   python test_setup.py > test_results.txt 2>&1
   ```

### What to Include in Bug Reports

1. **Environment:**
   - OS and version
   - Python version
   - Package versions (pip list)

2. **Configuration:**
   - Region being used
   - Model being used
   - Resource allocation

3. **Error:**
   - Full error message
   - Stack trace
   - When it occurs (always, sometimes, specific queries)

4. **Logs:**
   - Terminal output
   - Cloud Run logs (if deployed)
   - Test results

5. **What you tried:**
   - Steps to reproduce
   - Solutions attempted
   - Any changes made

---

## Still Having Issues?

If you've tried the solutions above and still have problems:

1. **Run the test suite** and share results
2. **Check Cloud Console** for any service outages
3. **Review all logs** carefully for clues
4. **Try the simplest possible setup** first
5. **Contact the AI Engineering team** with diagnostic info

Remember: Most issues are related to authentication, permissions, or configuration!
