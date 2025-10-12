"""
FastAPI Backend for Face Recognition Service
This service should be deployed separately (e.g., on a VPS, AWS EC2, or Railway)

Installation:
pip install fastapi uvicorn insightface onnxruntime numpy pillow requests

Run:
uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import insightface
from insightface.app import FaceAnalysis
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import os

app = FastAPI(title="Face Recognition API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize InsightFace
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))

class ExtractEmbeddingsRequest(BaseModel):
    image_url: str

class SearchFacesRequest(BaseModel):
    reference_embedding: list[float]
    threshold: float = 0.6
    event_id: str = None

class EmbeddingResponse(BaseModel):
    vector: list[float]
    confidence: float
    bbox: list[float]

@app.get("/")
def read_root():
    return {"status": "Face Recognition API is running"}

@app.post("/api/extract-embeddings")
async def extract_embeddings(request: ExtractEmbeddingsRequest):
    """Extract face embeddings from an image URL"""
    try:
        # Download image
        response = requests.get(request.image_url)
        image = Image.open(BytesIO(response.content))
        image_array = np.array(image)
        
        # Detect faces and extract embeddings
        faces = face_app.get(image_array)
        
        if len(faces) == 0:
            return {"embeddings": []}
        
        embeddings = []
        for face in faces:
            embeddings.append({
                "vector": face.embedding.tolist(),
                "confidence": float(face.det_score),
                "bbox": face.bbox.tolist()
            })
        
        return {"embeddings": embeddings}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-faces")
async def search_faces(request: SearchFacesRequest):
    """
    Search for similar faces in the database
    Note: This is a simplified version. In production, you would:
    1. Query your database for all embeddings (filtered by event_id if provided)
    2. Calculate cosine similarity with the reference embedding
    3. Return matches above the threshold
    """
    try:
        # TODO: Implement database query to get stored embeddings
        # For now, returning empty matches
        # In production, you would:
        # 1. Connect to your Supabase database
        # 2. Query face_embeddings table (filtered by event_id)
        # 3. Calculate similarity scores
        # 4. Return photo_ids with similarity > threshold
        
        reference_emb = np.array(request.reference_embedding)
        matches = []
        
        # Example similarity calculation (you need to implement database query):
        # for stored_embedding in database_embeddings:
        #     similarity = cosine_similarity(reference_emb, stored_embedding.vector)
        #     if similarity > request.threshold:
        #         matches.append({
        #             "photo_id": stored_embedding.photo_id,
        #             "similarity": similarity
        #         })
        
        return {"matches": matches}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
