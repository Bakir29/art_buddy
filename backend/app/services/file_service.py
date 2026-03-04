import os
import uuid
import base64
import aiofiles
from typing import Optional
from pathlib import Path

class FileService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "images").mkdir(exist_ok=True)
        (self.upload_dir / "artwork").mkdir(exist_ok=True)
    
    async def save_base64_image(self, base64_data: str, filename: Optional[str] = None) -> str:
        """Save base64 image data to file and return URL."""
        if not filename:
            filename = f"{uuid.uuid4().hex}.jpg"
        
        # Ensure filename has proper extension
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            filename += '.jpg'
        
        file_path = self.upload_dir / "artwork" / filename
        
        try:
            # Decode and save image
            image_data = base64.b64decode(base64_data)
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_data)
            
            # Return relative URL path
            return f"/uploads/artwork/{filename}"
            
        except Exception as e:
            raise ValueError(f"Failed to save image: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file by path."""
        try:
            full_path = self.upload_dir.parent / file_path.lstrip('/')
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, filename: str, category: str = "artwork") -> str:
        """Get URL for a file."""
        return f"/uploads/{category}/{filename}"
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours."""
        import time
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        for category_dir in ["images", "artwork"]:
            category_path = self.upload_dir / category_dir
            if category_path.exists():
                for file_path in category_path.iterdir():
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                        except Exception:
                            continue
