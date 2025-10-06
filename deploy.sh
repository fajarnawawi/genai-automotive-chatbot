#!/bin/bash

# Automotive Sales Analytics Chatbot - Quick Deploy Script
# This script automates the deployment to Google Cloud Run

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "=================================================="
    echo "$1"
    echo "=================================================="
    echo ""
}

# Check if required tools are installed
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first:"
        echo "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI found"
    
    # Check if logged in
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        print_error "Not logged in to gcloud. Please run: gcloud auth login"
        exit 1
    fi
    print_success "Authenticated with gcloud"
}

# Get configuration from user
get_configuration() {
    print_header "Configuration"
    
    # Project ID
    if [ -z "$PROJECT_ID" ]; then
        read -p "Enter your GCP Project ID: " PROJECT_ID
    fi
    
    # Set project
    gcloud config set project "$PROJECT_ID"
    print_info "Using project: $PROJECT_ID"
    
    # Region
    if [ -z "$REGION" ]; then
        REGION="us-central1"
        read -p "Enter deployment region [us-central1]: " input_region
        if [ ! -z "$input_region" ]; then
            REGION=$input_region
        fi
    fi
    print_info "Using region: $REGION"
    
    # Service name
    if [ -z "$SERVICE_NAME" ]; then
        SERVICE_NAME="automotive-chatbot"
        read -p "Enter service name [automotive-chatbot]: " input_service
        if [ ! -z "$input_service" ]; then
            SERVICE_NAME=$input_service
        fi
    fi
    print_info "Service name: $SERVICE_NAME"
    
    # Repository name
    if [ -z "$REPOSITORY_NAME" ]; then
        REPOSITORY_NAME="chatbot-images"
    fi
    
    # Image configuration
    IMAGE_NAME="automotive-chatbot"
    IMAGE_TAG="latest"
    IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"
    
    export PROJECT_ID REGION SERVICE_NAME REPOSITORY_NAME IMAGE_URI
}

# Enable required APIs
enable_apis() {
    print_header "Enabling Required APIs"
    
    apis=(
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "artifactregistry.googleapis.com"
        "aiplatform.googleapis.com"
        "bigquery.googleapis.com"
        "iam.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_info "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" || true
    done
    
    print_success "APIs enabled"
}

# Create service account
create_service_account() {
    print_header "Setting Up Service Account"
    
    SERVICE_ACCOUNT_NAME="chatbot-cloud-run-sa"
    SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Check if service account exists
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &> /dev/null; then
        print_warning "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
    else
        print_info "Creating service account..."
        gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
            --display-name="Chatbot Cloud Run Service Account" \
            --project="$PROJECT_ID"
        print_success "Service account created"
    fi
    
    # Grant permissions
    print_info "Granting permissions..."
    
    roles=(
        "roles/bigquery.dataViewer"
        "roles/bigquery.jobUser"
        "roles/aiplatform.user"
        "roles/run.invoker"
        "roles/logging.logWriter"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
            --role="$role" \
            --condition=None \
            > /dev/null 2>&1 || true
    done
    
    print_success "Permissions granted"
    
    export SERVICE_ACCOUNT_EMAIL
}

# Create Artifact Registry repository
create_repository() {
    print_header "Setting Up Artifact Registry"
    
    # Check if repository exists
    if gcloud artifacts repositories describe "$REPOSITORY_NAME" \
        --location="$REGION" --project="$PROJECT_ID" &> /dev/null; then
        print_warning "Repository already exists: $REPOSITORY_NAME"
    else
        print_info "Creating Artifact Registry repository..."
        gcloud artifacts repositories create "$REPOSITORY_NAME" \
            --repository-format=docker \
            --location="$REGION" \
            --description="Docker repository for chatbot application" \
            --project="$PROJECT_ID"
        print_success "Repository created"
    fi
    
    # Configure Docker authentication
    print_info "Configuring Docker authentication..."
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
    print_success "Docker authentication configured"
}

# Build and push image
build_and_push() {
    print_header "Building and Pushing Docker Image"
    
    print_info "Building image with Cloud Build..."
    print_info "Image URI: $IMAGE_URI"
    
    gcloud builds submit \
        --tag="$IMAGE_URI" \
        --project="$PROJECT_ID" \
        --timeout=20m
    
    print_success "Image built and pushed successfully"
}

# Update environment variables file
update_env_vars() {
    print_header "Updating Environment Variables"
    
    if [ -f "env-vars.yaml" ]; then
        # Update project ID in env-vars.yaml
        sed -i.bak "s/YOUR_PROJECT_ID/$PROJECT_ID/g" env-vars.yaml
        rm -f env-vars.yaml.bak
        print_success "Environment variables updated"
    else
        print_error "env-vars.yaml not found. Please create it from env-vars.yaml template."
        exit 1
    fi
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    print_header "Deploying to Cloud Run"
    
    print_info "Deploying service: $SERVICE_NAME"
    
    gcloud run deploy "$SERVICE_NAME" \
        --image="$IMAGE_URI" \
        --platform=managed \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT_EMAIL" \
        --memory=2Gi \
        --cpu=2 \
        --timeout=300 \
        --concurrency=80 \
        --min-instances=0 \
        --max-instances=10 \
        --allow-unauthenticated \
        --env-vars-file=env-vars.yaml \
        --project="$PROJECT_ID"
    
    print_success "Deployment complete!"
}

# Get service URL
get_service_url() {
    print_header "Service Information"
    
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format='value(status.url)' \
        --project="$PROJECT_ID")
    
    print_success "Service deployed successfully!"
    echo ""
    echo "📍 Service URL: $SERVICE_URL"
    echo ""
    echo "To view logs:"
    echo "  gcloud run services logs tail $SERVICE_NAME --region=$REGION"
    echo ""
    echo "To open in browser:"
    echo "  gcloud run services browse $SERVICE_NAME --region=$REGION"
    echo ""
}

# Main execution
main() {
    clear
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║   Automotive Sales Analytics Chatbot Deployer     ║"
    echo "║              Google Cloud Run                      ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    
    check_prerequisites
    get_configuration
    
    # Confirm deployment
    echo ""
    print_warning "About to deploy with the following configuration:"
    echo "  Project: $PROJECT_ID"
    echo "  Region: $REGION"
    echo "  Service: $SERVICE_NAME"
    echo "  Image: $IMAGE_URI"
    echo ""
    read -p "Continue with deployment? (y/N): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi
    
    enable_apis
    create_service_account
    create_repository
    build_and_push
    update_env_vars
    deploy_to_cloud_run
    get_service_url
    
    print_success "🎉 All done! Your chatbot is now live!"
}

# Run main function
main "$@"
