from fastapi import FastAPI, File, HTTPException
from typing import Annotated

from ml_service import get_prediction

app = FastAPI(title="Distributed AI System Master Node")


@app.get("/")
async def root_path():
    """Simple welcome route to verify the server is reachable."""
    return {
        "service": "Master Node API",
        "status": "online",
        "endpoints": ["/health", "/infer"]
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint. 
    In future weeks, you will update this to return the number 
    of connected worker nodes and their CPU/GPU loads.
    """
    return {
        "status": "healthy",
        "active_workers": 0,  
        "system_load": "normal"
    }


@app.post("/infer")
async def infer_endpoint(file: Annotated[bytes, File()]):
    """
    Receives an image, validates it, and processes the inference.
    Uses 'bytes' for fast memory loading, protected by a size limit.
    """
    
    MAX_FILE_SIZE = 5 * 1024 * 1024 
    file_size = len(file)
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Size: {file_size} bytes. Limit: 5MB."
        )

    result_class, confidence = get_prediction(file)
    
    return {
        "status": "success",
        "file_size_bytes": file_size,
        "prediction": result_class, 
        "confidence": confidence
    }