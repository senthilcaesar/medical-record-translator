from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict
import os
import uuid
import aiofiles
from datetime import datetime
import shutil

from app.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.ai_translator import AITranslator
from app.services.validators import FileValidator

router = APIRouter()

# Initialize services
pdf_processor = PDFProcessor()
ai_translator = AITranslator()
file_validator = FileValidator()

# In-memory storage for job status (in production, use Redis)
job_status = {}

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict:
    """
    Upload a medical document for translation.
    
    Args:
        file: The uploaded PDF file
        
    Returns:
        Job ID and initial status
    """
    try:
        # Validate the uploaded file
        await file_validator.validate_upload(file)
        file_validator.validate_content_type(file.content_type)
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save the file temporarily
        filename = file_validator.sanitize_filename(file.filename)
        file_path = os.path.join(settings.UPLOAD_DIR, f"{job_id}_{filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Initialize job status
        job_status[job_id] = {
            "status": "processing",
            "progress": 0,
            "filename": filename,
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
            "error": None
        }
        
        # Process the document in the background
        background_tasks.add_task(process_document, job_id, file_path)
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Document uploaded successfully. Processing started."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_document(job_id: str, file_path: str):
    """
    Process the document in the background.
    
    Args:
        job_id: Unique job identifier
        file_path: Path to the uploaded file
    """
    try:
        # Update status
        job_status[job_id]["progress"] = 20
        job_status[job_id]["status"] = "extracting_text"
        
        # Extract text from PDF
        extracted_text = pdf_processor.extract_text_from_pdf(file_path)
        
        if not extracted_text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        # Update status
        job_status[job_id]["progress"] = 40
        job_status[job_id]["status"] = "identifying_document_type"
        
        # Identify document type
        doc_type = pdf_processor.identify_document_type(extracted_text)
        
        # Update status
        job_status[job_id]["progress"] = 60
        job_status[job_id]["status"] = "translating"
        
        # Translate the document
        translation_result = await ai_translator.translate_document(extracted_text, doc_type)
        
        if not translation_result["success"]:
            raise ValueError(translation_result.get("error", "Translation failed"))
        
        # Update status
        job_status[job_id]["progress"] = 100
        job_status[job_id]["status"] = "completed"
        job_status[job_id]["result"] = {
            "document_type": doc_type,
            "translation": translation_result["translation"],
            "sections": translation_result["sections"],
            "original_text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        }
        
    except Exception as e:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["error"] = str(e)
        job_status[job_id]["progress"] = 0
    
    finally:
        # Clean up the uploaded file
        try:
            os.remove(file_path)
        except:
            pass

@router.get("/status/{job_id}")
async def get_job_status(job_id: str) -> Dict:
    """
    Get the status of a translation job.
    
    Args:
        job_id: The job identifier
        
    Returns:
        Current job status and progress
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]

@router.get("/result/{job_id}")
async def get_translation_result(job_id: str) -> Dict:
    """
    Get the translation result for a completed job.
    
    Args:
        job_id: The job identifier
        
    Returns:
        Translation result or error
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_status[job_id]
    
    if job["status"] == "processing":
        raise HTTPException(status_code=202, detail="Translation still in progress")
    
    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=f"Translation failed: {job['error']}")
    
    if job["status"] == "completed" and job["result"]:
        return {
            "job_id": job_id,
            "status": "completed",
            "result": job["result"]
        }
    
    raise HTTPException(status_code=500, detail="Unknown error occurred")

@router.delete("/job/{job_id}")
async def delete_job(job_id: str) -> Dict:
    """
    Delete a job and its results from memory.
    
    Args:
        job_id: The job identifier
        
    Returns:
        Deletion confirmation
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del job_status[job_id]
    
    return {"message": "Job deleted successfully"}

@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Medical Record Translator API",
        "version": "1.0.0"
    }
