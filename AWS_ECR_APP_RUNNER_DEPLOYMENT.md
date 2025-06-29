# AWS ECR & App Runner Deployment Guide

This guide provides detailed step-by-step instructions for deploying the Medical Record Translator application to AWS using Amazon Elastic Container Registry (ECR) and AWS App Runner.

## Prerequisites

- AWS CLI installed and configured with appropriate credentials
- Docker installed locally
- AWS account with permissions for ECR and App Runner
- OpenAI API key
- Domain name (optional, for custom domain)

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Amazon ECR    │     │   Amazon ECR    │     │  AWS Systems    │
│ Backend Image   │     │ Frontend Image  │     │    Manager      │
└────────┬────────┘     └────────┬────────┘     │ Parameter Store │
         │                       │               └────────┬────────┘
         │                       │                        │
    ┌────▼────────────────┐     ┌▼───────────────────┐   │
    │  App Runner Service │     │ App Runner Service  │   │
    │     (Backend)       │◄────┤    (Frontend)       │   │
    │  FastAPI + Python   │     │  Nginx + React     │   │
    └────────┬────────────┘     └────────────────────┘   │
             │                                            │
             │              ┌─────────────────┐           │
             └──────────────┤ Amazon ElastiCache │◄───────┘
                           │     (Redis)         │
                           └─────────────────────┘
```

## Step 1: Set Up AWS Resources

### 1.1 Create ECR Repositories

```bash
# Set your AWS region
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create ECR repositories
aws ecr create-repository \
    --repository-name medical-translator-backend \
    --region $AWS_REGION

aws ecr create-repository \
    --repository-name medical-translator-frontend \
    --region $AWS_REGION
```

### 1.2 Set Up ElastiCache Redis (Optional but Recommended)

```bash
# Create a subnet group for ElastiCache
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name medical-translator-subnet \
    --cache-subnet-group-description "Subnet group for medical translator" \
    --subnet-ids subnet-xxxxx subnet-yyyyy

# Create Redis cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id medical-translator-redis \
    --engine redis \
    --cache-node-type cache.t3.micro \
    --num-cache-nodes 1 \
    --cache-subnet-group-name medical-translator-subnet
```

### 1.3 Store Secrets in AWS Systems Manager Parameter Store

```bash
# Store OpenAI API Key
aws ssm put-parameter \
    --name "/medical-translator/openai-api-key" \
    --value "your-openai-api-key-here" \
    --type "SecureString" \
    --description "OpenAI API Key for Medical Translator"

# Store Redis URL (after ElastiCache is created)
aws ssm put-parameter \
    --name "/medical-translator/redis-url" \
    --value "redis://your-redis-endpoint.cache.amazonaws.com:6379" \
    --type "String" \
    --description "Redis URL for Medical Translator"
```

## Step 2: Build and Push Docker Images

### 2.1 Authenticate Docker to ECR

```bash
# Get ECR login token
aws ecr get-login-password --region $AWS_REGION | \
docker login --username AWS --password-stdin \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

### 2.2 Build and Push Backend Image

```bash
# Navigate to project root
cd /path/to/medical-record-translator

# Build backend image
docker build -t medical-translator-backend ./backend

# Tag for ECR
docker tag medical-translator-backend:latest \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-backend:latest

# Push to ECR
docker push \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-backend:latest
```

### 2.3 Build and Push Frontend Image

First, create a production nginx configuration:

```bash
# Create a production nginx config
cat > frontend/nginx.prod.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Security
        server_tokens off;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API proxy to backend App Runner service
        location /api/ {
            # This will be replaced with actual backend URL
            proxy_pass BACKEND_APP_RUNNER_URL/api/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 300;
            proxy_send_timeout 300;
            proxy_read_timeout 300;
        }

        # Static file caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # React app
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
EOF
```

Now build and push the frontend:

```bash
# Build frontend image
docker build -t medical-translator-frontend ./frontend

# Tag for ECR
docker tag medical-translator-frontend:latest \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-frontend:latest

# Push to ECR
docker push \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-frontend:latest
```

## Step 3: Create App Runner Services

### 3.1 Create Backend Service

Create `apprunner-backend.yaml`:

```yaml
version: 1.0
runtime: docker
build:
  commands:
    build:
      - echo "No build commands"
run:
  runtime-version: latest
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
    env: PORT
  env:
    - name: OPENAI_API_KEY
      value-from: "/medical-translator/openai-api-key"
    - name: REDIS_URL
      value-from: "/medical-translator/redis-url"
    - name: CORS_ORIGINS
      value: "https://your-frontend-domain.awsapprunner.com"
    - name: OPENAI_MODEL
      value: "gpt-4-turbo-preview"
```

Deploy backend service:

```bash
# Create App Runner service for backend
aws apprunner create-service \
    --service-name "medical-translator-backend" \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'$AWS_ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com/medical-translator-backend:latest",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentSecrets": {
                    "OPENAI_API_KEY": "arn:aws:ssm:'$AWS_REGION':'$AWS_ACCOUNT_ID':parameter/medical-translator/openai-api-key"
                },
                "RuntimeEnvironmentVariables": {
                    "REDIS_URL": "redis://your-redis-endpoint.cache.amazonaws.com:6379",
                    "CORS_ORIGINS": "https://your-frontend-domain.awsapprunner.com",
                    "OPENAI_MODEL": "gpt-4-turbo-preview"
                }
            },
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": false
    }' \
    --health-check-configuration '{
        "Protocol": "HTTP",
        "Path": "/api/v1/translate/health",
        "Interval": 10,
        "Timeout": 5,
        "HealthyThreshold": 2,
        "UnhealthyThreshold": 3
    }'
```

### 3.2 Get Backend Service URL

```bash
# Get the backend service URL
BACKEND_URL=$(aws apprunner describe-service \
    --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-backend'].ServiceArn" --output text) \
    --query "Service.ServiceUrl" \
    --output text)

echo "Backend URL: https://$BACKEND_URL"
```

### 3.3 Update Frontend Configuration and Rebuild

```bash
# Update nginx configuration with actual backend URL
sed -i "s|BACKEND_APP_RUNNER_URL|https://$BACKEND_URL|g" frontend/nginx.prod.conf

# Copy production config
cp frontend/nginx.prod.conf frontend/nginx.conf

# Rebuild frontend image with updated configuration
docker build -t medical-translator-frontend ./frontend

# Tag and push updated image
docker tag medical-translator-frontend:latest \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-frontend:latest

docker push \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-frontend:latest
```

### 3.4 Create Frontend Service

```bash
# Create App Runner service for frontend
aws apprunner create-service \
    --service-name "medical-translator-frontend" \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'$AWS_ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com/medical-translator-frontend:latest",
            "ImageConfiguration": {
                "Port": "80"
            },
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": false
    }' \
    --health-check-configuration '{
        "Protocol": "HTTP",
        "Path": "/health",
        "Interval": 10,
        "Timeout": 5,
        "HealthyThreshold": 2,
        "UnhealthyThreshold": 3
    }'
```

## Step 4: Configure Auto-Scaling

```bash
# Configure auto-scaling for backend
aws apprunner update-service \
    --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-backend'].ServiceArn" --output text) \
    --auto-scaling-configuration-arn $(aws apprunner create-auto-scaling-configuration \
        --auto-scaling-configuration-name "medical-translator-scaling" \
        --min-size 1 \
        --max-size 10 \
        --max-concurrency 100 \
        --query "AutoScalingConfiguration.AutoScalingConfigurationArn" \
        --output text)
```

## Step 5: Set Up Custom Domain (Optional)

### 5.1 Associate Custom Domain

```bash
# For frontend
aws apprunner associate-custom-domain \
    --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-frontend'].ServiceArn" --output text) \
    --domain-name "app.yourdomain.com"

# For backend API
aws apprunner associate-custom-domain \
    --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-backend'].ServiceArn" --output text) \
    --domain-name "api.yourdomain.com"
```

### 5.2 Update DNS Records

Add the provided CNAME records to your DNS provider.

## Step 6: Monitoring and Logs

### 6.1 View Service Logs

```bash
# View backend logs
aws logs tail /aws/apprunner/medical-translator-backend/service --follow

# View frontend logs
aws logs tail /aws/apprunner/medical-translator-frontend/service --follow
```

### 6.2 Set Up CloudWatch Alarms

```bash
# Create alarm for backend service
aws cloudwatch put-metric-alarm \
    --alarm-name "medical-translator-backend-errors" \
    --alarm-description "Alert on backend errors" \
    --metric-name "4xxStatusCode" \
    --namespace "AWS/AppRunner" \
    --statistic "Sum" \
    --period 300 \
    --threshold 10 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 1
```

## Step 7: CI/CD Pipeline (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS App Runner

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-east-1

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push backend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        run: |
          docker build -t $ECR_REGISTRY/medical-translator-backend:latest ./backend
          docker push $ECR_REGISTRY/medical-translator-backend:latest

      - name: Deploy to App Runner
        run: |
          aws apprunner start-deployment \
            --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-backend'].ServiceArn" --output text)

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Get backend URL
        id: backend-url
        run: |
          BACKEND_URL=$(aws apprunner describe-service \
            --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-backend'].ServiceArn" --output text) \
            --query "Service.ServiceUrl" \
            --output text)
          echo "url=https://$BACKEND_URL" >> $GITHUB_OUTPUT

      - name: Update nginx config
        run: |
          sed -i "s|BACKEND_APP_RUNNER_URL|${{ steps.backend-url.outputs.url }}|g" frontend/nginx.conf

      - name: Build and push frontend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        run: |
          docker build -t $ECR_REGISTRY/medical-translator-frontend:latest ./frontend
          docker push $ECR_REGISTRY/medical-translator-frontend:latest

      - name: Deploy to App Runner
        run: |
          aws apprunner start-deployment \
            --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='medical-translator-frontend'].ServiceArn" --output text)
```

## Troubleshooting

### Common Issues and Solutions

1. **ECR Login Failed**

   ```bash
   # Ensure AWS CLI is configured
   aws configure list

   # Check IAM permissions
   aws ecr describe-repositories
   ```

2. **App Runner Service Won't Start**

   - Check CloudWatch logs
   - Verify environment variables
   - Ensure health check endpoint is accessible
   - Check IAM role permissions

3. **Frontend Can't Connect to Backend**

   - Verify CORS settings in backend
   - Check nginx proxy configuration
   - Ensure backend URL is correct in nginx.conf

4. **Redis Connection Issues**
   - Verify ElastiCache security group allows App Runner
   - Check Redis endpoint URL
   - Test connection from App Runner VPC

### Useful Commands

```bash
# List all services
aws apprunner list-services

# Describe service details
aws apprunner describe-service --service-arn <service-arn>

# View service logs
aws logs tail /aws/apprunner/<service-name>/service --follow

# Force new deployment
aws apprunner start-deployment --service-arn <service-arn>

# Delete service
aws apprunner delete-service --service-arn <service-arn>
```

## Cost Optimization

1. **Use App Runner Pause/Resume**

   ```bash
   # Pause service when not in use
   aws apprunner pause-service --service-arn <service-arn>

   # Resume service
   aws apprunner resume-service --service-arn <service-arn>
   ```

2. **Right-size Resources**

   - Start with minimum configuration
   - Monitor usage and scale as needed
   - Use auto-scaling effectively

3. **Clean Up Unused Resources**
   - Delete old ECR images
   - Remove unused App Runner services
   - Clean up ElastiCache if not needed

## Security Best Practices

1. **Use IAM Roles**: App Runner services should use IAM roles, not access keys
2. **Encrypt Secrets**: Use AWS Systems Manager Parameter Store for sensitive data
3. **Enable VPC**: For production, use VPC connector for private resources
4. **Regular Updates**: Keep Docker images updated with security patches
5. **Monitor Access**: Use CloudTrail to audit API calls

## Next Steps

1. Set up monitoring dashboards in CloudWatch
2. Configure alerts for critical metrics
3. Implement backup strategy for Redis data
4. Set up WAF rules for additional security
5. Configure auto-deployment from your CI/CD pipeline

## Support Resources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/)
- [App Runner Pricing](https://aws.amazon.com/apprunner/pricing/)
