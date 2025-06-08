from fastapi import UploadFile, HTTPException
from typing import Optional
import os
from app.config import settings

class FileValidator:
    """Service for validating uploaded files."""
    
    @staticmethod
    async def validate_upload(file: UploadFile) -> None:
        """
        Validate an uploaded file.
        
        Args:
            file: The uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        # Check if file exists
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Move to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Check if file is empty
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    @staticmethod
    def validate_content_type(content_type: Optional[str]) -> None:
        """
        Validate the content type of the uploaded file.
        
        Args:
            content_type: The MIME type of the file
            
        Raises:
            HTTPException: If content type is invalid
        """
        allowed_content_types = ['application/pdf']
        
        if content_type not in allowed_content_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type. Expected: {', '.join(allowed_content_types)}"
            )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to prevent security issues.
        
        Args:
            filename: The original filename
            
        Returns:
            Sanitized filename
        """
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Remove any non-alphanumeric characters except dots, dashes, and underscores
        import re
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        
        # Ensure the filename is not empty
        if not filename:
            filename = 'document.pdf'
        
        return filename
