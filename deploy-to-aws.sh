#!/bin/bash

# AWS App Runner Deployment Script for Medical Record Translator
# This script automates the deployment process to AWS ECR and App Runner

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    print_status "Prerequisites check passed!"
}

# Set environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    # Get AWS account ID and region
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    export AWS_REGION=${AWS_REGION:-$(aws configure get region)}
    
    # Set default values
    export ECR_BACKEND_REPO="medical-translator-backend"
    export ECR_FRONTEND_REPO="medical-translator-frontend"
    export BACKEND_SERVICE_NAME="medical-translator-backend"
    export FRONTEND_SERVICE_NAME="medical-translator-frontend"
    
    print_status "AWS Account ID: $AWS_ACCOUNT_ID"
    print_status "AWS Region: $AWS_REGION"
}

# Create ECR repositories if they don't exist
create_ecr_repositories() {
    print_status "Creating ECR repositories..."
    
    # Create backend repository
    if ! aws ecr describe-repositories --repository-names $ECR_BACKEND_REPO --region $AWS_REGION &> /dev/null; then
        aws ecr create-repository --repository-name $ECR_BACKEND_REPO --region $AWS_REGION
        print_status "Created ECR repository: $ECR_BACKEND_REPO"
    else
        print_status "ECR repository already exists: $ECR_BACKEND_REPO"
    fi
    
    # Create frontend repository
    if ! aws ecr describe-repositories --repository-names $ECR_FRONTEND_REPO --region $AWS_REGION &> /dev/null; then
        aws ecr create-repository --repository-name $ECR_FRONTEND_REPO --region $AWS_REGION
        print_status "Created ECR repository: $ECR_FRONTEND_REPO"
    else
        print_status "ECR repository already exists: $ECR_FRONTEND_REPO"
    fi
}

# Login to ECR
ecr_login() {
    print_status "Logging in to Amazon ECR..."
    aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
}

# Build and push backend image
deploy_backend() {
    print_status "Building and pushing backend image..."
    
    # Build image
    docker build -t $ECR_BACKEND_REPO ./backend
    
    # Tag image
    docker tag $ECR_BACKEND_REPO:latest \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_BACKEND_REPO:latest
    
    # Push image
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_BACKEND_REPO:latest
    
    print_status "Backend image pushed successfully!"
}

# Build and push frontend image
deploy_frontend() {
    print_status "Building and pushing frontend image..."
    
    # Get backend URL if service exists
    BACKEND_ARN=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$BACKEND_SERVICE_NAME'].ServiceArn" --output text 2>/dev/null || echo "")
    
    if [ -n "$BACKEND_ARN" ]; then
        BACKEND_URL=$(aws apprunner describe-service --service-arn $BACKEND_ARN --query "Service.ServiceUrl" --output text)
        print_status "Found backend URL: https://$BACKEND_URL"
        
        # Update nginx configuration
        cp frontend/nginx.conf frontend/nginx.conf.bak
        sed -i "s|proxy_pass http://backend:8000/api/|proxy_pass https://$BACKEND_URL/api/|g" frontend/nginx.conf
    else
        print_warning "Backend service not found. Using default nginx configuration."
    fi
    
    # Build image
    docker build -t $ECR_FRONTEND_REPO ./frontend
    
    # Tag image
    docker tag $ECR_FRONTEND_REPO:latest \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_FRONTEND_REPO:latest
    
    # Push image
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_FRONTEND_REPO:latest
    
    # Restore original nginx.conf if it was modified
    if [ -f frontend/nginx.conf.bak ]; then
        mv frontend/nginx.conf.bak frontend/nginx.conf
    fi
    
    print_status "Frontend image pushed successfully!"
}

# Create or update App Runner services
create_app_runner_services() {
    print_status "Creating/updating App Runner services..."
    
    # Check if backend service exists
    BACKEND_ARN=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$BACKEND_SERVICE_NAME'].ServiceArn" --output text 2>/dev/null || echo "")
    
    if [ -z "$BACKEND_ARN" ]; then
        print_status "Creating backend App Runner service..."
        
        # Create backend service
        aws apprunner create-service \
            --service-name "$BACKEND_SERVICE_NAME" \
            --source-configuration "{
                \"ImageRepository\": {
                    \"ImageIdentifier\": \"$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_BACKEND_REPO:latest\",
                    \"ImageConfiguration\": {
                        \"Port\": \"8000\",
                        \"RuntimeEnvironmentVariables\": {
                            \"CORS_ORIGINS\": \"*\"
                        }
                    },
                    \"ImageRepositoryType\": \"ECR\"
                },
                \"AutoDeploymentsEnabled\": false
            }" \
            --health-check-configuration "{
                \"Protocol\": \"HTTP\",
                \"Path\": \"/api/v1/translate/health\",
                \"Interval\": 10,
                \"Timeout\": 5,
                \"HealthyThreshold\": 2,
                \"UnhealthyThreshold\": 3
            }"
    else
        print_status "Backend service already exists. Starting new deployment..."
        aws apprunner start-deployment --service-arn $BACKEND_ARN
    fi
    
    # Wait for backend to be ready
    print_status "Waiting for backend service to be ready..."
    sleep 30
    
    # Check if frontend service exists
    FRONTEND_ARN=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$FRONTEND_SERVICE_NAME'].ServiceArn" --output text 2>/dev/null || echo "")
    
    if [ -z "$FRONTEND_ARN" ]; then
        print_status "Creating frontend App Runner service..."
        
        # Create frontend service
        aws apprunner create-service \
            --service-name "$FRONTEND_SERVICE_NAME" \
            --source-configuration "{
                \"ImageRepository\": {
                    \"ImageIdentifier\": \"$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_FRONTEND_REPO:latest\",
                    \"ImageConfiguration\": {
                        \"Port\": \"80\"
                    },
                    \"ImageRepositoryType\": \"ECR\"
                },
                \"AutoDeploymentsEnabled\": false
            }" \
            --health-check-configuration "{
                \"Protocol\": \"HTTP\",
                \"Path\": \"/health\",
                \"Interval\": 10,
                \"Timeout\": 5,
                \"HealthyThreshold\": 2,
                \"UnhealthyThreshold\": 3
            }"
    else
        print_status "Frontend service already exists. Starting new deployment..."
        aws apprunner start-deployment --service-arn $FRONTEND_ARN
    fi
}

# Display service URLs
display_urls() {
    print_status "Retrieving service URLs..."
    
    # Get backend URL
    BACKEND_ARN=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$BACKEND_SERVICE_NAME'].ServiceArn" --output text)
    if [ -n "$BACKEND_ARN" ]; then
        BACKEND_URL=$(aws apprunner describe-service --service-arn $BACKEND_ARN --query "Service.ServiceUrl" --output text)
        print_status "Backend URL: ${GREEN}https://$BACKEND_URL${NC}"
    fi
    
    # Get frontend URL
    FRONTEND_ARN=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$FRONTEND_SERVICE_NAME'].ServiceArn" --output text)
    if [ -n "$FRONTEND_ARN" ]; then
        FRONTEND_URL=$(aws apprunner describe-service --service-arn $FRONTEND_ARN --query "Service.ServiceUrl" --output text)
        print_status "Frontend URL: ${GREEN}https://$FRONTEND_URL${NC}"
    fi
    
    echo ""
    print_status "Deployment complete! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Update your backend environment variables in App Runner console"
    echo "2. Add your OpenAI API key to AWS Systems Manager Parameter Store"
    echo "3. Configure Redis if needed"
    echo "4. Set up custom domains if desired"
}

# Main deployment flow
main() {
    echo "======================================"
    echo "Medical Record Translator AWS Deployment"
    echo "======================================"
    echo ""
    
    check_prerequisites
    setup_environment
    create_ecr_repositories
    ecr_login
    
    # Ask user what to deploy
    echo ""
    echo "What would you like to deploy?"
    echo "1) Backend only"
    echo "2) Frontend only"
    echo "3) Both (recommended for first deployment)"
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            deploy_backend
            ;;
        2)
            deploy_frontend
            ;;
        3)
            deploy_backend
            deploy_frontend
            ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
    
    create_app_runner_services
    display_urls
}

# Run main function
main