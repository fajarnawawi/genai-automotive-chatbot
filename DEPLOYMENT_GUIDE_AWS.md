# AWS Deployment Guide - Automotive Sales Analytics Chatbot

This guide walks you through deploying the Automotive Sales Analytics Chatbot on AWS infrastructure using Amazon Redshift, Amazon Bedrock (Claude), and Amazon ECS Fargate.

## Table of Contents
- [Prerequisites](#prerequisites)
- [AWS Services Overview](#aws-services-overview)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
- [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Tools
- **AWS CLI** (v2.0 or later)
  ```bash
  # Install AWS CLI
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
  ```

- **Docker** (v20.10 or later)
  ```bash
  # Verify Docker installation
  docker --version
  ```

- **AWS Account** with appropriate permissions

### AWS Permissions Required
Your AWS user/role needs permissions for:
- Amazon ECR (Elastic Container Registry)
- Amazon ECS (Elastic Container Service)
- Amazon Redshift
- Amazon Bedrock
- AWS IAM (for role creation)
- Amazon VPC
- Amazon CloudWatch
- AWS Secrets Manager (optional, for secure credential storage)

### Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region, and output format
```

---

## AWS Services Overview

| Service | Purpose | Cost Estimate |
|---------|---------|---------------|
| **Amazon Redshift** | Data warehouse for automotive sales data | ~$0.25/hour (dc2.large) |
| **Amazon Bedrock** | Claude AI model for natural language processing | ~$0.003/1K tokens |
| **Amazon ECS Fargate** | Serverless container compute | ~$0.04/hour (1 vCPU, 2GB RAM) |
| **Amazon ECR** | Container image registry | ~$0.10/GB-month |
| **Application Load Balancer** | Traffic distribution (optional) | ~$0.0225/hour |
| **CloudWatch** | Logging and monitoring | ~$0.50/GB ingested |

**Estimated Monthly Cost**: $200-400 (depending on usage)

---

## Quick Start

### 1. Enable Bedrock Model Access

Before deployment, enable Claude model access in Amazon Bedrock:

```bash
# Navigate to AWS Console > Bedrock > Model access
# Or use AWS CLI (if available in your region)
aws bedrock list-foundation-models --region us-east-1
```

**Required Models**:
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Recommended)
- `anthropic.claude-3-5-haiku-20241022-v1:0` (Alternative)

### 2. Set Up Redshift Cluster

Create a Redshift cluster with your automotive sales data:

```bash
# Option 1: Use AWS Console
# Navigate to Redshift > Clusters > Create cluster

# Option 2: Use AWS CLI
aws redshift create-cluster \
    --cluster-identifier automotive-cluster \
    --node-type dc2.large \
    --master-username admin \
    --master-user-password YourPassword123! \
    --cluster-type single-node \
    --publicly-accessible \
    --region us-east-1
```

**Important**: Note your cluster endpoint, database name, and credentials.

### 3. Update Configuration

Copy and edit the AWS environment template:

```bash
cp .env.aws.template .env.aws
nano .env.aws  # Edit with your AWS settings
```

**Key Configuration Values**:
```bash
AWS_REGION=us-east-1
REDSHIFT_HOST=your-cluster.us-east-1.redshift.amazonaws.com
REDSHIFT_DATABASE=automotive_data
REDSHIFT_USER=admin
REDSHIFT_PASSWORD=YourPassword123!  # Or use IAM authentication
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### 4. Run Automated Deployment

Execute the deployment script:

```bash
chmod +x deploy-aws.sh
./deploy-aws.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Create ECR repository
3. ✅ Build and push Docker image
4. ✅ Create IAM roles
5. ✅ Set up networking
6. ✅ Create ECS cluster
7. ✅ Deploy ECS service
8. ✅ Configure CloudWatch logging

**Deployment time**: ~10-15 minutes

### 5. Access Your Application

After deployment completes, access your application at:
```
http://[PUBLIC_IP]:8080
```

The public IP will be displayed at the end of the deployment script.

---

## Detailed Setup

### Step 1: Prepare Redshift Database

#### Load Sample Data
```sql
-- Connect to your Redshift cluster
psql -h your-cluster.us-east-1.redshift.amazonaws.com \
     -U admin -d automotive_data -p 5439

-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Load data from S3 (example)
COPY public.vehicles FROM 's3://your-bucket/vehicles.csv'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftS3Role'
CSV IGNOREHEADER 1;
```

#### Configure Network Access
1. Navigate to Redshift Console > Clusters
2. Select your cluster
3. Click "Properties" > "Network and security"
4. Edit VPC security group
5. Add inbound rule: PostgreSQL (5439) from ECS security group

### Step 2: Build and Test Locally

#### Local Development with AWS Services
```bash
# Install dependencies
pip install -r requirements-aws.txt

# Set environment variables
export $(cat .env.aws | xargs)

# Run locally
streamlit run app/main_aws.py
```

#### Test Redshift Connection
```python
# test_connection.py
from app.config_aws import config_aws
from app.database_aws import initialize_database

result = initialize_database()
print(result)
```

### Step 3: Deploy to AWS ECS

#### Manual Deployment (Alternative to Script)

**1. Create ECR Repository**
```bash
aws ecr create-repository \
    --repository-name automotive-chatbot \
    --region us-east-1
```

**2. Build and Push Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -f Dockerfile.aws -t automotive-chatbot:latest .

# Tag and push
docker tag automotive-chatbot:latest \
    123456789012.dkr.ecr.us-east-1.amazonaws.com/automotive-chatbot:latest

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/automotive-chatbot:latest
```

**3. Create IAM Roles**

See `deploy-aws.sh` for complete IAM role configurations. Key policies needed:
- ECS Task Execution Role
- ECS Task Role with Bedrock and Redshift permissions

**4. Create ECS Task Definition**

Use `env-vars-aws.yaml` as reference for environment variables.

**5. Create ECS Service**
```bash
aws ecs create-service \
    --cluster automotive-chatbot-cluster \
    --service-name automotive-chatbot-service \
    --task-definition automotive-chatbot \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## Configuration

### IAM Authentication for Redshift (Recommended)

Instead of using passwords, use IAM authentication:

**1. Update Configuration**
```bash
REDSHIFT_USE_IAM=true
REDSHIFT_CLUSTER_IDENTIFIER=automotive-cluster
```

**2. Attach IAM Policy to Task Role**
```json
{
  "Effect": "Allow",
  "Action": [
    "redshift:GetClusterCredentials",
    "redshift:DescribeClusters"
  ],
  "Resource": "*"
}
```

**3. Create Redshift User**
```sql
CREATE USER "IAM:automotive-chatbot-task-role" PASSWORD DISABLE;
GRANT ALL ON SCHEMA public TO "IAM:automotive-chatbot-task-role";
```

### Secrets Manager Integration

Store sensitive credentials in AWS Secrets Manager:

**1. Create Secret**
```bash
aws secretsmanager create-secret \
    --name automotive-chatbot/redshift \
    --secret-string '{"password":"YourPassword123!"}'
```

**2. Reference in Task Definition**
```json
{
  "name": "REDSHIFT_PASSWORD",
  "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:automotive-chatbot/redshift:password::"
}
```

### Bedrock Model Configuration

Available Claude models:

| Model ID | Use Case | Cost |
|----------|----------|------|
| `anthropic.claude-3-5-sonnet-20241022-v2:0` | Best balance of speed and capability | $0.003/1K tokens |
| `anthropic.claude-3-5-haiku-20241022-v1:0` | Fastest, most cost-effective | $0.0008/1K tokens |
| `anthropic.claude-3-opus-20240229-v1:0` | Most powerful for complex queries | $0.015/1K tokens |

---

## Deployment Options

### Option 1: ECS Fargate (Recommended)
- ✅ Serverless, no server management
- ✅ Auto-scaling capabilities
- ✅ Pay only for what you use
- ❌ Higher per-hour cost

**Use Case**: Production deployments, variable traffic

### Option 2: ECS EC2
- ✅ Lower cost for consistent workloads
- ✅ More control over infrastructure
- ❌ Requires server management
- ❌ Must provision capacity upfront

**Use Case**: High-traffic, steady workloads

### Option 3: AWS Lambda (Future)
- ✅ Event-driven, extreme scalability
- ✅ Pay per request
- ❌ 15-minute timeout limit
- ❌ Complex for Streamlit apps

**Use Case**: Batch processing, API endpoints

### Option 4: Application Load Balancer + Auto Scaling

Add ALB for production:

```bash
# Create target group
aws elbv2 create-target-group \
    --name automotive-chatbot-tg \
    --protocol HTTP \
    --port 8080 \
    --vpc-id vpc-xxx \
    --target-type ip

# Create load balancer
aws elbv2 create-load-balancer \
    --name automotive-chatbot-alb \
    --subnets subnet-xxx subnet-yyy \
    --security-groups sg-xxx
```

---

## Monitoring and Troubleshooting

### CloudWatch Logs

**View Real-time Logs**:
```bash
aws logs tail /aws/automotive-chatbot --follow
```

**Query Specific Errors**:
```bash
aws logs filter-log-events \
    --log-group-name /aws/automotive-chatbot \
    --filter-pattern "ERROR"
```

### ECS Service Health

**Check Service Status**:
```bash
aws ecs describe-services \
    --cluster automotive-chatbot-cluster \
    --services automotive-chatbot-service
```

**View Task Details**:
```bash
aws ecs list-tasks \
    --cluster automotive-chatbot-cluster \
    --service-name automotive-chatbot-service

aws ecs describe-tasks \
    --cluster automotive-chatbot-cluster \
    --tasks [TASK_ARN]
```

### Common Issues

#### Issue: "Failed to connect to Redshift"
**Solution**:
1. Check security group allows traffic from ECS tasks
2. Verify Redshift cluster is publicly accessible (or VPC peered)
3. Test credentials manually with `psql`

#### Issue: "Bedrock access denied"
**Solution**:
1. Verify model access is enabled in Bedrock console
2. Check IAM task role has `bedrock:InvokeModel` permission
3. Ensure you're using the correct model ID

#### Issue: "Container exits immediately"
**Solution**:
1. Check CloudWatch logs for error messages
2. Verify all environment variables are set correctly
3. Test Docker image locally first

### Performance Monitoring

**Set Up CloudWatch Alarms**:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name high-cpu-utilization \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold
```

---

## Cost Optimization

### 1. Use Redshift Pause/Resume
```bash
# Pause cluster when not in use
aws redshift pause-cluster --cluster-identifier automotive-cluster

# Resume when needed
aws redshift resume-cluster --cluster-identifier automotive-cluster
```

**Savings**: ~80% of Redshift costs

### 2. Use Fargate Spot
Update ECS service to use Fargate Spot for non-production:
```json
"capacityProviderStrategy": [
  {
    "capacityProvider": "FARGATE_SPOT",
    "weight": 1
  }
]
```

**Savings**: ~70% of compute costs

### 3. Optimize Bedrock Usage
- Use Claude Haiku for simple queries
- Implement caching for repeated queries
- Set appropriate max_tokens limits

### 4. Right-size Resources
Monitor and adjust:
- ECS task CPU/memory allocation
- Redshift cluster size
- CloudWatch log retention

### 5. Use Reserved Capacity
For production workloads:
- Redshift Reserved Instances: 40-70% savings
- Savings Plans for ECS: 50% savings

---

## Security Best Practices

### 1. Network Security
- ✅ Use VPC with private subnets
- ✅ Restrict security group rules
- ✅ Enable VPC Flow Logs
- ✅ Use AWS PrivateLink for Bedrock

### 2. Data Protection
- ✅ Enable encryption at rest (Redshift, ECR)
- ✅ Enable encryption in transit (SSL/TLS)
- ✅ Use AWS Secrets Manager for credentials
- ✅ Enable CloudTrail for audit logging

### 3. Access Control
- ✅ Use IAM roles, not access keys
- ✅ Implement least privilege principle
- ✅ Enable MFA for AWS console access
- ✅ Rotate credentials regularly

### 4. Compliance
- ✅ Enable AWS Config for compliance tracking
- ✅ Use AWS Security Hub for security findings
- ✅ Implement AWS WAF for web application firewall
- ✅ Regular security audits

---

## Next Steps

1. **Set up CI/CD Pipeline**
   - Use AWS CodePipeline for automated deployments
   - Integrate with GitHub for continuous delivery

2. **Implement Auto Scaling**
   - Configure ECS service auto scaling based on CPU/memory
   - Set up target tracking policies

3. **Add Custom Domain**
   - Use Route 53 for DNS management
   - Set up ACM certificate for HTTPS

4. **Enhance Monitoring**
   - Create custom CloudWatch dashboards
   - Set up SNS notifications for alerts
   - Integrate with PagerDuty or Slack

5. **Data Pipeline**
   - Set up AWS Glue for ETL
   - Use AWS Data Pipeline for data refresh
   - Implement incremental data loads

---

## Support and Resources

- **AWS Documentation**: https://docs.aws.amazon.com
- **Amazon Bedrock**: https://aws.amazon.com/bedrock
- **Amazon Redshift**: https://aws.amazon.com/redshift
- **AWS ECS**: https://aws.amazon.com/ecs

For issues or questions, refer to:
- AWS Support (if you have a support plan)
- AWS re:Post community forums
- Project GitHub repository

---

## License

This deployment guide is provided as-is for the Automotive Sales Analytics Chatbot project.
