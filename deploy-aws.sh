#!/bin/bash

#############################################################################
# AWS Deployment Script for Automotive Sales Analytics Chatbot
# This script deploys the application to AWS using:
# - Amazon ECR for container registry
# - Amazon ECS Fargate for serverless compute
# - Application Load Balancer for traffic distribution
# - Amazon Redshift for data warehouse
# - Amazon Bedrock for AI/ML
#############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_NAME="automotive-chatbot"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")

# Print functions
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first:"
        echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    print_success "AWS CLI is installed"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first:"
        echo "https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker is installed"

    # Check AWS credentials
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    print_success "AWS credentials configured (Account: $AWS_ACCOUNT_ID)"

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Create ECR repository
create_ecr_repository() {
    print_header "Setting up Amazon ECR"

    REPO_NAME="${PROJECT_NAME}"

    # Check if repository exists
    if aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" &> /dev/null; then
        print_success "ECR repository '$REPO_NAME' already exists"
    else
        print_info "Creating ECR repository..."
        aws ecr create-repository \
            --repository-name "$REPO_NAME" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        print_success "ECR repository created: $REPO_NAME"
    fi

    ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"
    print_success "ECR URI: $ECR_URI"
}

# Build and push Docker image
build_and_push_image() {
    print_header "Building and Pushing Docker Image"

    # Login to ECR
    print_info "Logging in to Amazon ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    print_success "Logged in to ECR"

    # Build image
    print_info "Building Docker image..."
    IMAGE_TAG="latest"
    docker build -f Dockerfile.aws -t "${PROJECT_NAME}:${IMAGE_TAG}" .
    print_success "Docker image built"

    # Tag image
    print_info "Tagging image..."
    docker tag "${PROJECT_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"
    docker tag "${PROJECT_NAME}:${IMAGE_TAG}" "${ECR_URI}:$(date +%Y%m%d-%H%M%S)"
    print_success "Image tagged"

    # Push image
    print_info "Pushing image to ECR..."
    docker push "${ECR_URI}:${IMAGE_TAG}"
    docker push "${ECR_URI}:$(date +%Y%m%d-%H%M%S)"
    print_success "Image pushed to ECR"
}

# Create IAM roles
create_iam_roles() {
    print_header "Setting up IAM Roles"

    # ECS Task Execution Role
    EXECUTION_ROLE_NAME="${PROJECT_NAME}-execution-role"
    print_info "Creating ECS Task Execution Role..."

    if aws iam get-role --role-name "$EXECUTION_ROLE_NAME" &> /dev/null; then
        print_success "Execution role already exists"
    else
        # Create trust policy
        cat > /tmp/ecs-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

        aws iam create-role \
            --role-name "$EXECUTION_ROLE_NAME" \
            --assume-role-policy-document file:///tmp/ecs-trust-policy.json

        aws iam attach-role-policy \
            --role-name "$EXECUTION_ROLE_NAME" \
            --policy-arn "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"

        print_success "Execution role created"
    fi

    # ECS Task Role (for application permissions)
    TASK_ROLE_NAME="${PROJECT_NAME}-task-role"
    print_info "Creating ECS Task Role..."

    if aws iam get-role --role-name "$TASK_ROLE_NAME" &> /dev/null; then
        print_success "Task role already exists"
    else
        aws iam create-role \
            --role-name "$TASK_ROLE_NAME" \
            --assume-role-policy-document file:///tmp/ecs-trust-policy.json

        # Create and attach policy for Redshift and Bedrock access
        cat > /tmp/task-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "redshift:GetClusterCredentials",
        "redshift:DescribeClusters"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

        aws iam put-role-policy \
            --role-name "$TASK_ROLE_NAME" \
            --policy-name "${PROJECT_NAME}-permissions" \
            --policy-document file:///tmp/task-policy.json

        print_success "Task role created with Bedrock and Redshift permissions"
    fi

    EXECUTION_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${EXECUTION_ROLE_NAME}"
    TASK_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${TASK_ROLE_NAME}"
}

# Create VPC and networking (simplified)
setup_networking() {
    print_header "Setting up Networking"

    # Use default VPC for simplicity
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region "$AWS_REGION")

    if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
        print_error "No default VPC found. Please create a VPC first."
        exit 1
    fi

    print_success "Using VPC: $VPC_ID"

    # Get subnets
    SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region "$AWS_REGION")
    SUBNET_IDS=(${SUBNETS})

    print_success "Found ${#SUBNET_IDS[@]} subnets"

    # Create security group
    SG_NAME="${PROJECT_NAME}-sg"

    # Check if security group exists
    SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text --region "$AWS_REGION" 2>/dev/null || echo "None")

    if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
        print_info "Creating security group..."
        SG_ID=$(aws ec2 create-security-group \
            --group-name "$SG_NAME" \
            --description "Security group for $PROJECT_NAME" \
            --vpc-id "$VPC_ID" \
            --region "$AWS_REGION" \
            --query 'GroupId' \
            --output text)

        # Allow inbound HTTP traffic
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port 8080 \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"

        # Allow inbound HTTPS traffic
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port 443 \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"

        print_success "Security group created: $SG_ID"
    else
        print_success "Security group already exists: $SG_ID"
    fi
}

# Create ECS cluster
create_ecs_cluster() {
    print_header "Setting up ECS Cluster"

    CLUSTER_NAME="${PROJECT_NAME}-cluster"

    if aws ecs describe-clusters --clusters "$CLUSTER_NAME" --region "$AWS_REGION" --query "clusters[0].clusterName" --output text 2>/dev/null | grep -q "$CLUSTER_NAME"; then
        print_success "ECS cluster already exists"
    else
        print_info "Creating ECS cluster..."
        aws ecs create-cluster \
            --cluster-name "$CLUSTER_NAME" \
            --region "$AWS_REGION" \
            --capacity-providers FARGATE FARGATE_SPOT \
            --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
        print_success "ECS cluster created: $CLUSTER_NAME"
    fi
}

# Create CloudWatch log group
create_log_group() {
    print_header "Setting up CloudWatch Logs"

    LOG_GROUP="/aws/${PROJECT_NAME}"

    if aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --region "$AWS_REGION" | grep -q "$LOG_GROUP"; then
        print_success "Log group already exists"
    else
        print_info "Creating CloudWatch log group..."
        aws logs create-log-group \
            --log-group-name "$LOG_GROUP" \
            --region "$AWS_REGION"
        print_success "Log group created: $LOG_GROUP"
    fi
}

# Register ECS task definition
register_task_definition() {
    print_header "Registering ECS Task Definition"

    print_info "Creating task definition..."

    # Note: Update these with your actual Redshift details
    cat > /tmp/task-definition.json <<EOF
{
  "family": "${PROJECT_NAME}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "${EXECUTION_ROLE_ARN}",
  "taskRoleArn": "${TASK_ROLE_ARN}",
  "containerDefinitions": [
    {
      "name": "${PROJECT_NAME}",
      "image": "${ECR_URI}:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "AWS_REGION", "value": "${AWS_REGION}"},
        {"name": "REDSHIFT_USE_IAM", "value": "true"},
        {"name": "REDSHIFT_HOST", "value": "your-cluster.${AWS_REGION}.redshift.amazonaws.com"},
        {"name": "REDSHIFT_DATABASE", "value": "automotive_data"},
        {"name": "REDSHIFT_SCHEMA", "value": "public"},
        {"name": "REDSHIFT_USER", "value": "admin"},
        {"name": "REDSHIFT_CLUSTER_IDENTIFIER", "value": "automotive-cluster"},
        {"name": "BEDROCK_MODEL_ID", "value": "anthropic.claude-3-5-sonnet-20241022-v2:0"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/aws/${PROJECT_NAME}",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

    aws ecs register-task-definition \
        --cli-input-json file:///tmp/task-definition.json \
        --region "$AWS_REGION" > /dev/null

    print_success "Task definition registered"
}

# Create ECS service
create_ecs_service() {
    print_header "Creating ECS Service"

    SERVICE_NAME="${PROJECT_NAME}-service"

    # Check if service exists
    if aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$SERVICE_NAME" --region "$AWS_REGION" --query "services[0].serviceName" --output text 2>/dev/null | grep -q "$SERVICE_NAME"; then
        print_info "Service already exists. Updating..."
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$SERVICE_NAME" \
            --force-new-deployment \
            --region "$AWS_REGION" > /dev/null
        print_success "Service updated"
    else
        print_info "Creating ECS service..."

        aws ecs create-service \
            --cluster "$CLUSTER_NAME" \
            --service-name "$SERVICE_NAME" \
            --task-definition "${PROJECT_NAME}" \
            --desired-count 1 \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS[0]},${SUBNET_IDS[1]}],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
            --region "$AWS_REGION" > /dev/null

        print_success "ECS service created"
    fi
}

# Print deployment summary
print_summary() {
    print_header "Deployment Summary"

    echo -e "${GREEN}✓ Deployment completed successfully!${NC}\n"

    print_info "Resources Created:"
    echo "  • ECR Repository: $ECR_URI"
    echo "  • ECS Cluster: $CLUSTER_NAME"
    echo "  • ECS Service: ${PROJECT_NAME}-service"
    echo "  • CloudWatch Logs: /aws/${PROJECT_NAME}"
    echo ""

    print_warning "Next Steps:"
    echo "  1. Update Redshift credentials in the task definition"
    echo "  2. Ensure Redshift security group allows connections from ECS"
    echo "  3. Enable Bedrock model access in your AWS account"
    echo "  4. (Optional) Set up Application Load Balancer for better access"
    echo "  5. Monitor logs: aws logs tail /aws/${PROJECT_NAME} --follow"
    echo ""

    # Get task public IP
    print_info "Fetching service endpoint..."
    sleep 5
    TASK_ARN=$(aws ecs list-tasks --cluster "$CLUSTER_NAME" --service-name "${PROJECT_NAME}-service" --region "$AWS_REGION" --query 'taskArns[0]' --output text)

    if [ "$TASK_ARN" != "None" ] && [ -n "$TASK_ARN" ]; then
        ENI_ID=$(aws ecs describe-tasks --cluster "$CLUSTER_NAME" --tasks "$TASK_ARN" --region "$AWS_REGION" --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)

        if [ -n "$ENI_ID" ] && [ "$ENI_ID" != "None" ]; then
            PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids "$ENI_ID" --region "$AWS_REGION" --query 'NetworkInterfaces[0].Association.PublicIp' --output text)

            if [ -n "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "None" ]; then
                echo -e "\n${GREEN}Application URL: http://${PUBLIC_IP}:8080${NC}"
                echo -e "${YELLOW}Note: It may take a few minutes for the service to become available${NC}\n"
            fi
        fi
    fi
}

# Main deployment flow
main() {
    print_header "AWS Deployment Script - Automotive Analytics Chatbot"

    echo "This script will deploy the application to AWS using:"
    echo "  • Amazon ECR (Container Registry)"
    echo "  • Amazon ECS Fargate (Serverless Compute)"
    echo "  • Amazon Redshift (Data Warehouse)"
    echo "  • Amazon Bedrock (AI/ML)"
    echo ""
    echo "Region: $AWS_REGION"
    echo "Account: $AWS_ACCOUNT_ID"
    echo ""

    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi

    check_prerequisites
    create_ecr_repository
    build_and_push_image
    create_iam_roles
    setup_networking
    create_ecs_cluster
    create_log_group
    register_task_definition
    create_ecs_service
    print_summary
}

# Run main function
main
