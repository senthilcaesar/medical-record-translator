# Docker Setup for Medical Record Translator

This document provides instructions for building and running the Medical Record Translator application using Docker.

## Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- OpenAI API key

## Quick Start

1. **Clone the repository and navigate to the project directory**

2. **Set up environment variables**

   ```bash
   # Copy the example environment file
   cp backend/.env.example backend/.env

   # Edit the .env file and add your OpenAI API key
   # OPENAI_API_KEY=your_api_key_here
   ```

3. **Build and run the containers**

   ```bash
   # Using Make (recommended)
   make dev

   # Or using docker-compose directly
   docker-compose build
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Docker Configuration Files

### Backend Dockerfile

- Multi-stage build for optimized image size
- Non-root user for security
- Health check endpoint included
- PyMuPDF and all dependencies pre-installed

### Frontend Dockerfile

- Multi-stage build with Node.js and Nginx
- Production-optimized React build
- Nginx configured with security headers and compression
- Static asset caching enabled

### Docker Compose Files

- `docker-compose.yml`: Development configuration
- `docker-compose.prod.yml`: Production-ready configuration with resource limits

## Available Commands

### Using Make

```bash
make help           # Show all available commands
make build          # Build development containers
make up             # Start containers
make down           # Stop containers
make logs           # View container logs
make clean          # Remove all containers and volumes
make shell-backend  # Access backend container shell
make shell-frontend # Access frontend container shell
make health         # Check service health
```

### Using Docker Compose

```bash
# Development
docker-compose build
docker-compose up -d
docker-compose logs -f
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Backend

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: GPT model to use (default: gpt-4-turbo-preview)
- `REDIS_URL`: Redis connection URL (default: redis://redis:6379)
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:3000)
- `UPLOAD_DIR`: Directory for file uploads (default: /app/uploads)

### Frontend

- `NODE_ENV`: Node environment (default: production)

## Deployment to AWS App Runner

### Backend Deployment

1. Build the backend image:

   ```bash
   docker build -t medical-translator-backend:latest ./backend
   ```

2. Tag and push to Amazon ECR:

   ```bash
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com
   docker tag medical-translator-backend:latest your-account-id.dkr.ecr.your-region.amazonaws.com/medical-translator-backend:latest
   docker push your-account-id.dkr.ecr.your-region.amazonaws.com/medical-translator-backend:latest
   ```

3. Create App Runner service using the pushed image

### Frontend Deployment

1. Build the frontend image:

   ```bash
   docker build -t medical-translator-frontend:latest ./frontend
   ```

2. Update `frontend/nginx.conf` with your backend App Runner URL:

   ```nginx
   location /api/ {
       proxy_pass https://your-backend-app-runner-url.awsapprunner.com/api/;
   }
   ```

3. Rebuild and push to ECR following the same process as backend

## Troubleshooting

### Container won't start

- Check logs: `docker-compose logs [service-name]`
- Verify environment variables are set correctly
- Ensure ports 3000 and 8000 are not in use

### API connection issues

- Verify backend is running: `curl http://localhost:8000/api/v1/translate/health`
- Check CORS settings in backend environment
- Ensure frontend nginx.conf has correct proxy settings

### Memory issues

- Increase Docker Desktop memory allocation
- Use production compose file with resource limits
- Monitor with: `docker stats`

### File upload issues

- Check upload directory permissions
- Verify volume mounts are correct
- Ensure MAX_FILE_SIZE setting is appropriate

## Security Considerations

1. **Non-root containers**: Both frontend and backend run as non-root users
2. **Environment variables**: Never commit `.env` files with real API keys
3. **Network isolation**: Containers communicate on internal network
4. **Security headers**: Nginx configured with security headers
5. **Resource limits**: Production compose file includes CPU/memory limits

## Performance Optimization

1. **Multi-stage builds**: Reduces final image size
2. **Layer caching**: Optimized Dockerfile order for faster rebuilds
3. **Nginx caching**: Static assets cached for 1 year
4. **Gzip compression**: Enabled for text-based assets
5. **Health checks**: Automatic container restart on failure

## Monitoring

- Backend health: `http://localhost:8000/api/v1/translate/health`
- Frontend health: `http://localhost:3000/health`
- Container stats: `docker stats`
- Logs: `docker-compose logs -f [service-name]`

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [Nginx Documentation](https://nginx.org/en/docs/)
