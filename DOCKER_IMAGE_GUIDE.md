# Creating Docker Images for Medical Record Translator

This guide explains how to create Docker container images for the Medical Record Translator application.

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed on your machine
- Access to the project source code

## Building Images Individually

### Backend Image

```bash
# Navigate to the backend directory
cd backend

# Build the image
docker build -t medical-translator-backend:latest .

# Verify the image was created
docker images | grep medical-translator-backend
```

### Frontend Image

```bash
# Navigate to the frontend directory
cd frontend

# Build the image using the production Dockerfile
docker build -t medical-translator-frontend:latest -f Dockerfile .

# Verify the image was created
docker images | grep medical-translator-frontend
```

## Building Images with Docker Compose

Docker Compose can build all your images at once:

### For Development Images
```bash
# From the project root directory
docker-compose build

# Or using the batch script
docker-run.bat build
```

### For Production Images
```bash
# From the project root directory
docker-compose -f docker-compose.prod.yml build

# Or using the batch script
docker-run.bat build prod
```

## Tagging and Pushing Images to a Registry

If you want to share your images or deploy them to a cloud service:

```bash
# Tag the images (replace 'yourusername' with your Docker Hub username or registry URL)
docker tag medical-translator-backend:latest yourusername/medical-translator-backend:latest
docker tag medical-translator-frontend:latest yourusername/medical-translator-frontend:latest

# Login to Docker Hub or your registry
docker login

# Push the images to Docker Hub or your registry
docker push yourusername/medical-translator-backend:latest
docker push yourusername/medical-translator-frontend:latest
```

## Running Containers from Your Images

After building the images, you can run containers:

### Running Backend Container
```bash
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key \
  -e OPENAI_MODEL=gpt-4-turbo-preview \
  -e CORS_ORIGINS=http://localhost \
  -e REDIS_URL=redis://redis:6379 \
  --name medical-translator-backend \
  medical-translator-backend:latest
```

### Running Frontend Container
```bash
docker run -d -p 80:80 \
  -e VITE_API_URL=http://localhost:8000 \
  --name medical-translator-frontend \
  medical-translator-frontend:latest
```

### Running Redis Container
```bash
docker run -d -p 6379:6379 \
  --name medical-translator-redis \
  -v redis_data:/data \
  redis:7-alpine
```

## Creating a Docker Network

For the containers to communicate with each other, create a network:

```bash
# Create a network
docker network create medical-translator-network

# Run containers with the network
docker run -d --network medical-translator-network --name medical-translator-redis -v redis_data:/data redis:7-alpine
docker run -d --network medical-translator-network --name medical-translator-backend -p 8000:8000 -e REDIS_URL=redis://medical-translator-redis:6379 [other env vars] medical-translator-backend:latest
docker run -d --network medical-translator-network --name medical-translator-frontend -p 80:80 medical-translator-frontend:latest
```

## Using Docker Compose (Recommended)

The easiest way to manage all containers is using Docker Compose:

```bash
# For development
docker-compose up -d

# For production
docker-compose -f docker-compose.prod.yml up -d
```

This will build the images if they don't exist and start all containers with the correct network configuration.