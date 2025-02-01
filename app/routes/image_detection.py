from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
# from app.services.detection_service import process_image

router = APIRouter()

@router.post("/image")
async def detect_objects(file: UploadFile = File(...)):
    try:
        # Read uploaded image
        image_bytes = await file.read()
        
        # Process image and detect objects
        # results = await process_image(image_bytes)
        results = ''
        
        return {
            "detected_objects": results,
            "total_objects": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))