# 🚀 AWS Deployment Quick Start Guide

This guide provides the fastest way to deploy your Medical Record Translator application to AWS using App Runner.

## Prerequisites Checklist

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Docker installed and running
- [ ] OpenAI API key ready
- [ ] Project cloned locally

## 🎯 Quick Deploy (5 minutes)

### Option 1: Automated Deployment Script

```bash
# Make the script executable (already done)
chmod +x deploy-to-aws.sh

# Run the deployment script
./deploy-to-aws.sh
```

The script will:

1. Check prerequisites
2. Create ECR repositories
3. Build and push Docker images
4. Create App Runner services
5. Display your application URLs

### Option 2: Manual Quick Deploy

```bash
# Set environment variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repositories
aws ecr create-repository --repository-name medical-translator-backend --region $AWS_REGION
aws ecr create-repository --repository-name medical-translator-frontend --region $AWS_REGION

# Build and push backend
docker build -t medical-translator-backend ./backend
docker tag medical-translator-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-backend:latest

# Build and push frontend
docker build -t medical-translator-frontend ./frontend
docker tag medical-translator-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-frontend:latest
```

## 🔧 Post-Deployment Configuration

### 1. Add OpenAI API Key

```bash
# Store your OpenAI API key securely
aws ssm put-parameter \
    --name "/medical-translator/openai-api-key" \
    --value "your-openai-api-key-here" \
    --type "SecureString"
```

### 2. Update Backend Environment Variables

Go to AWS App Runner Console → Select your backend service → Configuration → Configure service

Add these environment variables:

- `OPENAI_API_KEY`: (Reference from Parameter Store) `/medical-translator/openai-api-key`
- `OPENAI_MODEL`: `gpt-4-turbo-preview`
- `CORS_ORIGINS`: `https://your-frontend-url.awsapprunner.com`

### 3. Update Frontend to Point to Backend

After backend is deployed:

1. Get backend URL from App Runner console
2. Update `frontend/nginx.conf` to replace `http://backend:8000` with your backend URL
3. Rebuild and redeploy frontend:
   ```bash
   ./deploy-to-aws.sh
   # Choose option 2 (Frontend only)
   ```

## 📊 Verify Deployment

### Check Service Health

```bash
# Get service URLs
aws apprunner list-services --query "ServiceSummaryList[*].[ServiceName,ServiceUrl]" --output table

# Check backend health
curl https://your-backend-url.awsapprunner.com/api/v1/translate/health

# Check frontend
curl https://your-frontend-url.awsapprunner.com/health
```

### View Logs

```bash
# Backend logs
aws logs tail /aws/apprunner/medical-translator-backend/service --follow

# Frontend logs
aws logs tail /aws/apprunner/medical-translator-frontend/service --follow
```

## 💰 Cost Estimates

### App Runner Pricing (per service)

- **Provisioned compute**: ~$0.007/hour when running
- **Request charges**: $0.000025 per request
- **Data transfer**: First 1GB free, then $0.09/GB

### Monthly Estimates

- **Minimal usage** (< 1000 requests/month): ~$10-20/month
- **Moderate usage** (10,000 requests/month): ~$30-50/month
- **High usage** (100,000+ requests/month): ~$100-200/month

### Cost Optimization Tips

1. Pause services when not in use:
   ```bash
   aws apprunner pause-service --service-arn <service-arn>
   ```
2. Use auto-scaling effectively
3. Monitor usage with AWS Cost Explorer

## 🛠️ Troubleshooting Quick Fixes

### Issue: "ECR login failed"

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Re-configure if needed
aws configure
```

### Issue: "App Runner service unhealthy"

```bash
# Check logs
aws logs tail /aws/apprunner/<service-name>/service --follow

# Verify health endpoint
docker run -p 8000:8000 medical-translator-backend
curl http://localhost:8000/api/v1/translate/health
```

### Issue: "Frontend can't reach backend"

1. Check CORS settings in backend environment
2. Verify nginx proxy configuration
3. Ensure both services are running

### Issue: "OpenAI API errors"

1. Verify API key in Parameter Store
2. Check API key permissions
3. Monitor OpenAI usage/quotas

## 🔄 Update Deployment

To update your application after making changes:

```bash
# Quick update both services
./deploy-to-aws.sh
# Choose option 3 (Both)

# Or update specific service
docker build -t medical-translator-backend ./backend
docker tag medical-translator-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/medical-translator-backend:latest
aws apprunner start-deployment --service-arn <backend-service-arn>
```

## 🧹 Clean Up Resources

To avoid charges when not using the application:

```bash
# Pause services (keeps configuration, minimal charges)
aws apprunner pause-service --service-arn <backend-service-arn>
aws apprunner pause-service --service-arn <frontend-service-arn>

# Or delete everything (requires redeployment)
aws apprunner delete-service --service-arn <backend-service-arn>
aws apprunner delete-service --service-arn <frontend-service-arn>
aws ecr delete-repository --repository-name medical-translator-backend --force
aws ecr delete-repository --repository-name medical-translator-frontend --force
```

## 📚 Next Steps

1. **Set up monitoring**: Create CloudWatch dashboards
2. **Configure alerts**: Set up SNS notifications for errors
3. **Add custom domain**: Use Route 53 or your DNS provider
4. **Enable auto-deployment**: Set up GitHub Actions CI/CD
5. **Implement caching**: Add Redis via ElastiCache

## 🆘 Getting Help

- **AWS App Runner Issues**: Check [AWS App Runner docs](https://docs.aws.amazon.com/apprunner/)
- **Docker Issues**: Verify Docker daemon is running
- **Application Issues**: Check CloudWatch logs
- **Cost Concerns**: Use AWS Cost Explorer and set up billing alerts

---

**Pro Tip**: Save your commonly used AWS commands in your shell aliases:

```bash
echo "alias deploy-medical='cd /path/to/medical-record-translator && ./deploy-to-aws.sh'" >> ~/.bashrc
```

Happy deploying! 🎉
