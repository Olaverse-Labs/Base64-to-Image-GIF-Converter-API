from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import base64
import io
import os
import tempfile
from PIL import Image, ImageSequence
import uuid

app = FastAPI(
    title="Base64 to GIF Converter API",
    description="Convert base64 encoded images to GIF files with customizable parameters",
    version="1.0.0"
)

class Base64ToGifRequest(BaseModel):
    base64Images: List[str]
    width: int = 256
    height: int = 256
    transparent: bool = False
    loop: int = 0
    duration: int = 100

class Base64ToImageRequest(BaseModel):
    base64Image: str
    width: Optional[int] = None
    height: Optional[int] = None
    format: str = "PNG"  # PNG, JPEG, BMP, TIFF, WebP
    quality: int = 95  # For JPEG format (1-100)

@app.get("/")
async def root():
    return {
        "message": "Base64 to Image Converter API",
        "endpoints": {
            "convert_to_gif": "/convert-gif",
            "convert_to_image": "/convert-image"
        },
        "methods": "POST"
    }

@app.post("/convert-gif")
async def convert_base64_to_gif(request: Base64ToGifRequest):
    """
    Convert base64 encoded images to a GIF file
    
    - **base64Images**: List of base64 encoded image strings
    - **width**: Width of the output GIF (default: 256)
    - **height**: Height of the output GIF (default: 256)
    - **transparent**: Enable transparency (default: False)
    - **loop**: Number of loops (0 for infinite, default: 0)
    - **duration**: Duration between frames in milliseconds (default: 100)
    """
    try:
        # Debug: Print received values
        print(f"DEBUG: Received request - width: {request.width}, height: {request.height}, loop: {request.loop}, duration: {request.duration}, transparent: {request.transparent}")
        
        # Validate input
        if not request.base64Images:
            raise HTTPException(status_code=400, detail="base64Images list cannot be empty")
        
        # Check for None values and provide better error messages
        if request.width is None:
            raise HTTPException(status_code=400, detail="Width cannot be null")
        if request.height is None:
            raise HTTPException(status_code=400, detail="Height cannot be null")
        if request.duration is None:
            raise HTTPException(status_code=400, detail="Duration cannot be null")
        if request.loop is None:
            raise HTTPException(status_code=400, detail="Loop cannot be null")
        
        # Ensure all values are integers
        try:
            width = int(request.width)
            height = int(request.height)
            duration = int(request.duration)
            loop = int(request.loop)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid numeric values: {str(e)}")
        
        if width <= 0 or height <= 0:
            raise HTTPException(status_code=400, detail="Width and height must be positive integers")
        
        if duration <= 0:
            raise HTTPException(status_code=400, detail="Duration must be a positive integer")
        
        if loop < 0:
            raise HTTPException(status_code=400, detail="Loop count must be non-negative")
        
        # Process images
        images = []
        for i, base64_str in enumerate(request.base64Images):
            try:
                # Remove data URL prefix if present
                if base64_str.startswith('data:image'):
                    base64_str = base64_str.split(',')[1]
                
                # Decode base64
                image_data = base64.b64decode(base64_str)
                image = Image.open(io.BytesIO(image_data))
                
                # Convert to RGBA if transparency is enabled, otherwise RGB
                if request.transparent:
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                else:
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                
                # Resize image
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                images.append(image)
                
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid base64 image at index {i}: {str(e)}"
                )
        
        if not images:
            raise HTTPException(status_code=400, detail="No valid images found")
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filename = f"converted_{uuid.uuid4().hex}.gif"
        filepath = os.path.join(temp_dir, filename)
        
        # Save as GIF
        try:
            if len(images) == 1:
                # Single image
                save_kwargs = {
                    'format': 'GIF',
                    'loop': loop
                }
                if request.transparent:
                    save_kwargs['transparency'] = 0
                
                images[0].save(filepath, **save_kwargs)
            else:
                # Multiple images - create animation
                save_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'append_images': images[1:],
                    'duration': duration,
                    'loop': loop
                }
                if request.transparent:
                    save_kwargs['transparency'] = 0
                
                images[0].save(filepath, **save_kwargs)
        except Exception as save_error:
            raise HTTPException(
                status_code=500, 
                detail=f"Error saving GIF: {str(save_error)}. Parameters: loop={loop}, duration={duration}, transparent={request.transparent}"
            )
        
        return FileResponse(
            path=filepath,
            media_type='image/gif',
            filename=filename,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/convert-image")
async def convert_base64_to_image(request: Base64ToImageRequest):
    """
    Convert a single base64 encoded image to various image formats
    
    - **base64Image**: Base64 encoded image string
    - **width**: Width of the output image (optional, maintains aspect ratio if only width specified)
    - **height**: Height of the output image (optional, maintains aspect ratio if only height specified)
    - **format**: Output format (PNG, JPEG, BMP, TIFF, WebP, default: PNG)
    - **quality**: JPEG quality (1-100, default: 95, only applies to JPEG format)
    """
    try:
        # Validate input
        if not request.base64Image:
            raise HTTPException(status_code=400, detail="base64Image cannot be empty")
        
        if request.width is not None and request.width <= 0:
            raise HTTPException(status_code=400, detail="Width must be a positive integer")
        
        if request.height is not None and request.height <= 0:
            raise HTTPException(status_code=400, detail="Height must be a positive integer")
        
        if request.quality < 1 or request.quality > 100:
            raise HTTPException(status_code=400, detail="Quality must be between 1 and 100")
        
        # Validate format
        valid_formats = ["PNG", "JPEG", "BMP", "TIFF", "WebP"]
        if request.format.upper() not in valid_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid format. Supported formats: {', '.join(valid_formats)}"
            )
        
        try:
            # Remove data URL prefix if present
            base64_str = request.base64Image
            if base64_str.startswith('data:image'):
                base64_str = base64_str.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_str)
            image = Image.open(io.BytesIO(image_data))
            
            # Resize image if dimensions are specified
            if request.width is not None or request.height is not None:
                original_width, original_height = image.size
                
                if request.width is not None and request.height is not None:
                    # Both dimensions specified
                    new_size = (request.width, request.height)
                elif request.width is not None:
                    # Only width specified, maintain aspect ratio
                    ratio = request.width / original_width
                    new_size = (request.width, int(original_height * ratio))
                else:
                    # Only height specified, maintain aspect ratio
                    ratio = request.height / original_height
                    new_size = (int(original_width * ratio), request.height)
                
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            filename = f"converted_{uuid.uuid4().hex}.{request.format.lower()}"
            filepath = os.path.join(temp_dir, filename)
            
            # Save image with appropriate format and options
            save_kwargs = {}
            if request.format.upper() == "JPEG":
                # Convert to RGB for JPEG
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                save_kwargs['quality'] = request.quality
                save_kwargs['optimize'] = True
            
            image.save(filepath, format=request.format.upper(), **save_kwargs)
            
            # Determine MIME type
            mime_types = {
                "PNG": "image/png",
                "JPEG": "image/jpeg",
                "BMP": "image/bmp",
                "TIFF": "image/tiff",
                "WebP": "image/webp"
            }
            
            return FileResponse(
                path=filepath,
                media_type=mime_types[request.format.upper()],
                filename=filename,
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid base64 image: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 