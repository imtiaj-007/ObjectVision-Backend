from ultralytics import YOLO
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import numpy as np
import io

router = APIRouter()

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)

    def detect_objects(self, image_bytes):
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform detection
        results = self.model(image)
        
        # Process and format results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detections.append({
                    'class': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].tolist()
                })
        
        return detections

@router.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        detector = ObjectDetector()
        results = detector.detect_objects(image_bytes)
        
        return {
            "detected_objects": results,
            "total_objects": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))