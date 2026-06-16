from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from typing import List

from .scheduler import process_batch


app = FastAPI(title="Distributed AI System Master Node")


@app.get("/")
async def root_path():
    """Serves a simple HTML UI."""
    content = """
    <body>
    <h2>Distributed AI - Batch Upload Test</h2>
    <form action="/infer" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)


@app.get("/health")
async def health_check():
    """
    Health check endpoint. 
    """
    return {
        "status": "healthy",
        "active_workers": 0,  
        "system_load": "normal"
    }


@app.post("/infer")
async def infer_endpoint(files: List[UploadFile] = File(...)):
    """
    Receives an image, validates it, and forwards it to the gRPC worker node.
    """
    MAX_FILE_SIZE = 5 * 1024 * 1024 
    max_file_size = max([f.size for f in files])
    
    if max_file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
    if max_file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"One of the uploaded file is too large. Size: {max_file_size} bytes. Limit: 5MB."
        )

    try:
        # Our scheduling logic for batch split is here
        final_sorted_results = await process_batch(files)

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to communicate with worker node: {str(e)}"
        )
    
    return final_sorted_results