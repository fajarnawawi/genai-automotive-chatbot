# Google Cloud Run Deployment Guide

## Overview

This guide walks through deploying the Automotive Sales Analytics Chatbot to Google Cloud Run, a fully managed serverless platform.

## Prerequisites

### Required Tools
- Google Cloud SDK (`gcloud` CLI) installed and configured
- Docker installed (for local testing)
- Active Google Cloud Project with billing enabled

### Required APIs
Enable the following APIs in your project:

```bash
# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  iam.googleapis.com
```

## Step 1: Prepare Service Account

### Create Service Account

```bash
# Set variables
export PROJECT_ID="your-project-id"
export SERVICE_ACCOUNT_NAME="chatbot-cloud-run-sa"
export SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
  --display-name="Chatbot Cloud Run Service Account" \
  --project=${PROJECT_ID}
```

### Grant Required Permissions

```bash
# BigQuery Data Viewer - to read data
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/bigquery.dataViewer"

# BigQuery Job User - to run queries
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/bigquery.jobUser"

# Vertex AI User - to use Gemini
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/aiplatform.user"

# Cloud Run Invoker - to invoke the service
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/run.invoker"

# Logs Writer - for logging
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/logging.logWriter"
```

## Step 2: Create Artifact Registry Repository

```bash
# Set variables
export REGION="us-central1"
export REPOSITORY_NAME="chatbot-images"

# Create repository
gcloud artifacts repositories create ${REPOSITORY_NAME} \
  --repository-format=docker \
  --location=${REGION} \
  --description="Docker repository for chatbot application"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

## Step 3: Build and Push Docker Image

### Option A: Using Cloud Build (Recommended)

```bash
# Set variables
export IMAGE_NAME="automotive-chatbot"
export IMAGE_TAG="latest"
export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

# Navigate to cloud directory
cd /path/to/chatbot/cloud

# Build using Cloud Build
gcloud builds submit \
  --tag=${IMAGE_URI} \
  --project=${PROJECT_ID}
```

### Option B: Build Locally and Push

```bash
# Build Docker image locally
docker build -t ${IMAGE_URI} .

# Test locally (optional)
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=${PROJECT_ID} \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
  ${IMAGE_URI}

# Push to Artifact Registry
docker push ${IMAGE_URI}
```

## Step 4: Configure Environment Variables

Update `env-vars.yaml` with your project details:

```yaml
GCP_PROJECT_ID: "your-actual-project-id"
GCP_LOCATION: "us-central1"
BIGQUERY_DATASET: "automotive_data"
BIGQUERY_LOCATION: "US"
GEMINI_MODEL: "gemini-2.0-flash-lite-001"
GEMINI_TEMPERATURE: "0.1"
GEMINI_MAX_OUTPUT_TOKENS: "2048"
GEMINI_TOP_P: "0.95"
GEMINI_TOP_K: "40"
MAX_CHAT_HISTORY: "10"
LOG_LEVEL: "INFO"
SQL_AGENT_MAX_ITERATIONS: "15"
SQL_AGENT_MAX_EXECUTION_TIME: "100"
SQL_TOP_K_RESULTS: "10"
SESSION_TIMEOUT_MINUTES: "30"
```

## Step 5: Deploy to Cloud Run

### Initial Deployment

```bash
# Set variables
export SERVICE_NAME="automotive-chatbot"
export REGION="us-central1"

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URI} \
  --platform=managed \
  --region=${REGION} \
  --service-account=${SERVICE_ACCOUNT_EMAIL} \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10 \
  --allow-unauthenticated \
  --env-vars-file=env-vars.yaml \
  --project=${PROJECT_ID}
```

### Deployment with Custom Settings

```bash
# Deploy with specific settings
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URI} \
  --platform=managed \
  --region=${REGION} \
  --service-account=${SERVICE_ACCOUNT_EMAIL} \
  --memory=4Gi \
  --cpu=4 \
  --timeout=600 \
  --concurrency=100 \
  --min-instances=1 \
  --max-instances=20 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID}" \
  --set-env-vars="BIGQUERY_DATASET=automotive_data" \
  --set-env-vars="GEMINI_MODEL=gemini-2.0-flash-lite-001" \
  --allow-unauthenticated \
  --project=${PROJECT_ID}
```

## Step 6: Verify Deployment

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --format='value(status.url)' \
  --project=${PROJECT_ID})

echo "Service URL: ${SERVICE_URL}"

# Test service health
curl -I ${SERVICE_URL}/_stcore/health

# Open in browser
gcloud run services browse ${SERVICE_NAME} --region=${REGION}
```

## Configuration Options

### Memory and CPU

Recommended configurations based on usage:

**Development/Testing:**
```bash
--memory=2Gi --cpu=2
```

**Production (Low Traffic):**
```bash
--memory=2Gi --cpu=2 --min-instances=1 --max-instances=5
```

**Production (High Traffic):**
```bash
--memory=4Gi --cpu=4 --min-instances=2 --max-instances=20
```

### Concurrency

- **Default**: 80 concurrent requests per instance
- **Low memory usage**: Increase to 100-200
- **High memory usage**: Decrease to 40-60

### Timeout

- **Default**: 300 seconds (5 minutes)
- **Complex queries**: 600 seconds (10 minutes)
- **Maximum**: 3600 seconds (60 minutes)

## Security Configuration

### Require Authentication

```bash
# Deploy with authentication required
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URI} \
  --region=${REGION} \
  --no-allow-unauthenticated \
  [other options]

# Grant access to specific users
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
  --region=${REGION} \
  --member="user:alice@example.com" \
  --role="roles/run.invoker"
```

### Configure VPC Connector (Optional)

For private BigQuery datasets:

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create chatbot-connector \
  --region=${REGION} \
  --range=10.8.0.0/28

# Deploy with VPC connector
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URI} \
  --region=${REGION} \
  --vpc-connector=chatbot-connector \
  [other options]
```

## Monitoring and Logging

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID}

# View recent logs
gcloud run services logs read ${SERVICE_NAME} \
  --region=${REGION} \
  --limit=50
```

### View Metrics

```bash
# Open Cloud Console Metrics
gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --format="value(metadata.name)" | \
xargs -I {} echo "https://console.cloud.google.com/run/detail/${REGION}/{}/metrics?project=${PROJECT_ID}"
```

### Set Up Alerts

```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Chatbot High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

## Updating the Service

### Update with New Image

```bash
# Build new image
gcloud builds submit --tag=${IMAGE_URI}

# Deploy update
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URI} \
  --region=${REGION} \
  --project=${PROJECT_ID}
```

### Update Environment Variables Only

```bash
# Update single variable
gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --set-env-vars="LOG_LEVEL=DEBUG"

# Update multiple variables
gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --update-env-vars="GEMINI_MODEL=gemini-2.0-flash-lite-001,GEMINI_TEMPERATURE=0.2"

# Update from file
gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --env-vars-file=env-vars.yaml
```

### Rollback to Previous Revision

```bash
# List revisions
gcloud run revisions list \
  --service=${SERVICE_NAME} \
  --region=${REGION}

# Rollback to specific revision
gcloud run services update-traffic ${SERVICE_NAME} \
  --region=${REGION} \
  --to-revisions=REVISION_NAME=100
```

## Cost Optimization

### Use Minimum Instances Carefully

```bash
# For development: no minimum instances
--min-instances=0

# For production: use minimum instances to reduce cold starts
--min-instances=1  # Costs ~$40-60/month

# For high availability: use 2+ minimum instances
--min-instances=2  # Costs ~$80-120/month
```

### CPU Allocation

```bash
# CPU allocated only during request processing (default, cost-effective)
--cpu-throttling

# CPU always allocated (faster, more expensive)
--no-cpu-throttling
```

## Troubleshooting

### Issue: Service won't start

**Check logs:**
```bash
gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --limit=100
```

**Common causes:**
- Missing environment variables
- Service account lacks permissions
- BigQuery dataset not accessible
- Vertex AI API not enabled

### Issue: Timeout errors

**Solution:**
```bash
# Increase timeout
gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --timeout=600
```

### Issue: Out of memory

**Solution:**
```bash
# Increase memory
gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --memory=4Gi
```

### Issue: Cold starts too slow

**Solutions:**
1. Use minimum instances:
```bash
gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --min-instances=1
```

2. Optimize Docker image size
3. Use startup CPU boost:
```bash
--cpu-boost
```

## CI/CD Integration

### Using Cloud Build Triggers

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/chatbot-images/automotive-chatbot:$COMMIT_SHA', '.']
  
  # Push the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/chatbot-images/automotive-chatbot:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'automotive-chatbot'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/chatbot-images/automotive-chatbot:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/chatbot-images/automotive-chatbot:$COMMIT_SHA'
```

## Custom Domain Setup

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service=${SERVICE_NAME} \
  --domain=chatbot.yourdomain.com \
  --region=${REGION}

# Verify domain ownership in Cloud Console
```

## Cleanup

```bash
# Delete service
gcloud run services delete ${SERVICE_NAME} --region=${REGION}

# Delete images
gcloud artifacts docker images list \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}

gcloud artifacts docker images delete \
  ${IMAGE_URI} \
  --delete-tags

# Delete repository
gcloud artifacts repositories delete ${REPOSITORY_NAME} \
  --location=${REGION}

# Delete service account
gcloud iam service-accounts delete ${SERVICE_ACCOUNT_EMAIL}
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Best Practices for Cloud Run](https://cloud.google.com/run/docs/best-practices)
