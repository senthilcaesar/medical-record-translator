# Medical Record Translator - Docker Setup

This document provides instructions on how to containerize and run the Medical Record Translator application using Docker.

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed on your machine
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine (usually comes with Docker Desktop)

## Project Structure

The application consists of three main components:
- **Backend**: A FastAPI application that handles the translation of medical records
- **Frontend**: A React application that provides the user interface
- **Redis**: Used for caching and session management

## Running the Application

### Development Mode

Development mode includes hot reloading for both frontend and backend, which is useful during development.

```bash
# Using the provided script (Windows)
docker-run.bat dev

# Or using Docker Compose directly
docker-compose up
```

### Production Mode

1. First, create a `.env` file in the root directory based on the `.env.prod.example` template:

```bash
# Copy the example file
copy .env.prod.example .env

# Edit the .env file and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

2. Build and run the production containers:

```bash
# Using the provided script (Windows)
docker-run.bat build prod
docker-run.bat prod

# Or using Docker Compose directly
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000

## Managing Containers

### Viewing Logs

```bash
# Using the provided script (Windows)
docker-run.bat logs prod  # For production
docker-run.bat logs       # For development

# Or using Docker Compose directly
docker-compose -f docker-compose.prod.yml logs -f  # For production
docker-compose logs -f                            # For development
```

### Stopping Containers

```bash
# Using the provided script (Windows)
docker-run.bat down prod  # For production
docker-run.bat down       # For development

# Or using Docker Compose directly
docker-compose -f docker-compose.prod.yml down  # For production
docker-compose down                            # For development
```

## Configuration

### Environment Variables

The application uses environment variables for configuration. The main variables are:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: The OpenAI model to use (default: gpt-4-turbo-preview)
- `CORS_ORIGINS`: Allowed origins for CORS (default: http://localhost)
- `API_URL`: The URL of the backend API (default: http://localhost:8000)

These variables can be set in the `.env` file for production or passed directly to Docker Compose.

## Docker Images

### Backend

The backend image is built from `backend/Dockerfile` and includes:
- Python 3.11 with required dependencies
- FastAPI application code
- Configuration for connecting to OpenAI API and Redis

### Frontend

The frontend has two Dockerfiles:
- `frontend/Dockerfile.dev`: Used for development with hot reloading
- `frontend/Dockerfile`: Used for production, builds the React app and serves it with Nginx

## Volumes

The application uses Docker volumes for:
- Redis data persistence
- In development mode, source code directories are mounted for hot reloading

## Networking

The containers communicate with each other through Docker's internal network:
- Frontend can access the backend at `http://backend:8000`
- Backend can access Redis at `redis:6379`

## Troubleshooting

### Common Issues

1. **OpenAI API Key not working**
   - Ensure your API key is correctly set in the `.env` file
   - Check the backend logs for any authentication errors

2. **Containers not starting**
   - Check Docker logs for errors: `docker-compose logs`
   - Ensure all required ports are available (80, 8000, 6379)

3. **Frontend not connecting to backend**
   - Verify the `API_URL` environment variable is set correctly
   - Check CORS configuration in the backend

4. **File upload issues**
   - Ensure the upload directory exists and has proper permissions
   - Check file size limits in the backend configuration