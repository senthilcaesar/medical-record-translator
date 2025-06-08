from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import translate

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Medical Record Translator API...")
    # Create upload directory if it doesn't exist
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    # Shutdown
    print("Shutting down Medical Record Translator API...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for translating medical records into plain English",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Include routers
app.include_router(
    translate.router,
    prefix=f"{settings.API_V1_STR}/translate",
    tags=["translate"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Medical Record Translator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/translate/health"
    }

# API info endpoint
@app.get("/api/v1/info")
async def api_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "description": "Translate medical records into plain English",
        "endpoints": {
            "upload": f"{settings.API_V1_STR}/translate/upload",
            "status": f"{settings.API_V1_STR}/translate/status/{{job_id}}",
            "result": f"{settings.API_V1_STR}/translate/result/{{job_id}}",
            "health": f"{settings.API_V1_STR}/translate/health"
        },
        "supported_formats": list(settings.ALLOWED_EXTENSIONS),
        "max_file_size_mb": settings.MAX_FILE_SIZE / 1024 / 1024
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
