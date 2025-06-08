import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "Medical Record Translator"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # File Upload Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".pdf"}
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    
    # Security
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Redis Configuration (for job status tracking)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    JOB_EXPIRY = 3600  # 1 hour
    
    # Google Cloud Storage (optional for production)
    GCS_BUCKET = os.getenv("GCS_BUCKET", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 10

settings = Settings()
