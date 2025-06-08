# Medical Record Translator

A web application that helps patients understand their medical records by translating complex medical terminology into plain English using AI.

## Features

- **PDF Upload**: Upload lab results and prescriptions in PDF format
- **AI-Powered Translation**: Uses OpenAI GPT-4 to translate medical jargon
- **Structured Output**: Organized sections for easy understanding
- **Privacy-Focused**: No data persistence, files are deleted after processing
- **Responsive Design**: Works on desktop and mobile devices

## Architecture Overview

### Frontend (React + Vite)

The frontend is a single-page application built with React and Vite that provides:

- **User Interface**: Clean, modern UI built with React components and styled with Tailwind CSS
- **File Upload**: Drag-and-drop file upload using react-dropzone
- **API Communication**: Axios-based API client for backend communication
- **Real-time Updates**: Polling mechanism to track translation progress
- **State Management**: React hooks for local state management

Key Components:

- `FileUpload.jsx`: Handles PDF file selection and validation
- `LoadingSpinner.jsx`: Shows processing progress with percentage
- `TranslationResults.jsx`: Displays translated content in organized sections
- `App.jsx`: Main application component managing overall state

### Backend (Python FastAPI)

The backend is a RESTful API service that handles:

- **File Processing**: Validates and extracts text from PDF files using PyMuPDF
- **Document Classification**: Identifies document type (lab results vs prescription)
- **AI Translation**: Sends extracted text to OpenAI GPT-4 with specialized prompts
- **Async Processing**: Background job processing for non-blocking operations
- **Status Tracking**: In-memory job status tracking (Redis-ready for production)

Key Services:

- `pdf_processor.py`: Extracts and cleans text from PDFs
- `ai_translator.py`: Manages OpenAI API calls with custom medical prompts
- `validators.py`: Ensures file security and validity
- `translate.py`: API endpoints for upload, status checking, and results

### How Frontend and Backend Coordinate

1. **File Upload Flow**:

   - User selects a PDF file in the frontend
   - Frontend sends file to `/api/v1/translate/upload` endpoint
   - Backend returns a unique `job_id` immediately
   - Frontend starts polling for status updates

2. **Processing Flow**:

   - Backend processes file asynchronously in background
   - Updates job status: `extracting_text` → `identifying_document_type` → `translating` → `completed`
   - Frontend polls `/api/v1/translate/status/{job_id}` every second
   - Progress percentage is displayed to user

3. **Results Flow**:

   - Once status is `completed`, frontend fetches results from `/api/v1/translate/result/{job_id}`
   - Results include structured translation with sections
   - Frontend displays results in organized, readable format

4. **API Proxy Configuration**:
   - Vite dev server proxies `/api` requests to `http://localhost:8000`
   - This avoids CORS issues during development
   - In production, both can be served from same domain

## Tech Stack

### Backend

- **Python FastAPI**: High-performance async web framework
- **PyMuPDF**: PDF text extraction library
- **OpenAI API**: GPT-4 for medical translation
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI
- **Docker**: Containerization for deployment

### Frontend

- **React 18**: UI library with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Dropzone**: Drag-and-drop file uploads
- **React Toastify**: User notifications
- **React Markdown**: Render formatted results

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key
- Docker (optional, for containerized deployment)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd medical-record-translator
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Quick Start Guide

#### Step 1: Set up the Backend

1. Open a terminal and navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a Python virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file and add your OpenAI API key
# Open .env in your editor and replace 'your_openai_api_key_here' with your actual key
```

5. Start the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will start at `http://localhost:8000`. You can view the API documentation at `http://localhost:8000/docs`.

#### Step 2: Set up the Frontend

1. Open a **new terminal** and navigate to the frontend directory:

```bash
cd frontend
```

2. Install Node.js dependencies:

```bash
npm install
```

3. Start the frontend development server:

```bash
npm run dev
```

The frontend will start at `http://localhost:3000`.

#### Step 3: Use the Application

1. Open your browser and go to `http://localhost:3000`
2. You'll see the Medical Record Translator interface
3. Upload a PDF file (lab results or prescription)
4. Wait for the translation to complete
5. Review the results in plain English

### Using Docker Compose (Alternative)

If you prefer using Docker:

1. Make sure Docker and Docker Compose are installed
2. Create a `.env` file in the root directory with your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

3. Run the application:

```bash
docker-compose up --build
```

This will start both frontend and backend services automatically.

### Troubleshooting

**Backend Issues:**

- If you get "ModuleNotFoundError", make sure your virtual environment is activated
- If you get "OpenAI API key not configured", check your .env file
- If port 8000 is already in use, change it in the uvicorn command and update frontend proxy

**Frontend Issues:**

- If you get "node: command not found", install Node.js from https://nodejs.org
- If you get "vite: command not found", run `npm install` again
- If the frontend can't connect to backend, ensure backend is running on port 8000

**General Issues:**

- Make sure both terminals (backend and frontend) are running simultaneously
- Check that your OpenAI API key is valid and has credits
- Ensure your PDF files are under 10MB

## Usage

1. **Upload a Medical Document**: Click or drag a PDF file containing lab results or a prescription
2. **Wait for Processing**: The app will extract text, identify the document type, and translate it
3. **Review Results**: Read the plain English translation organized in clear sections
4. **Download or Start New**: Download the translation or upload another document

## API Endpoints

- `POST /api/v1/translate/upload` - Upload a PDF for translation
- `GET /api/v1/translate/status/{job_id}` - Check translation status
- `GET /api/v1/translate/result/{job_id}` - Get translation results
- `GET /api/v1/translate/health` - Health check endpoint

## Project Structure

```
medical-record-translator/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration settings
│   │   ├── routers/          # API routes
│   │   ├── services/         # Business logic
│   │   └── prompts/          # AI prompts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── App.jsx          # Main application
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml
```

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview
UPLOAD_DIR=/tmp/uploads
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Security Considerations

- Files are automatically deleted after processing
- No user data is stored permanently
- API rate limiting is implemented
- File size limits (10MB) prevent abuse
- Only PDF files are accepted

## Deployment

### Google Cloud Run

1. Build and push the Docker image:

```bash
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/medical-translator-backend
```

2. Deploy to Cloud Run:

```bash
gcloud run deploy medical-translator-backend \
  --image gcr.io/YOUR_PROJECT_ID/medical-translator-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. Deploy frontend to Firebase Hosting or Cloud Storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for educational purposes only. Always consult with healthcare providers for medical advice.

## Disclaimer

This application is designed to help patients better understand their medical documents but should not replace professional medical advice. Always consult with your healthcare provider for medical interpretations and decisions.
