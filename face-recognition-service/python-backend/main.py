"""
FastAPI Backend for Face Recognition Service with Multi-Upload Support
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import os
import sys
import tempfile
import cv2
import requests

# Import engine.py from parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import engine

app = FastAPI(title="Face Recognition API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ExtractEmbeddingsRequest(BaseModel):
    images: List[str]  # list of URLs or Base64 strings

class EmbeddingResponse(BaseModel):
    vector: list[float]
    confidence: float
    bbox: list[float]

@app.get("/")
def read_root():
    return {"status": "Face Recognition API is running"}

@app.post("/api/extract-embeddings")
async def extract_embeddings(request: Request):
    """
    Extract embeddings for multiple images.
    Supports image URLs or Base64 images.
    """
    # Prepare input normalization
    all_results = []
    print("request",request)
    # return all_results

    # Normalize request body to a list of image strings
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    images_list: List[str] = []
    if isinstance(body, dict) and "images" in body and isinstance(body["images"], list):
        images_list = body["images"]
    elif isinstance(body, list):
        images_list = body
    else:
        raise HTTPException(status_code=422, detail="Body must be { images: string[] } or a JSON array of strings")

    total_images = len(images_list)
    for idx, img_input in enumerate(images_list):
        print(f"Processing image {idx+1}/{total_images}")

        try:
            # Load image
            if isinstance(img_input, str) and img_input.startswith("data:image"):
                header, encoded = img_input.split(",", 1)
                image = Image.open(BytesIO(base64.b64decode(encoded)))
            else:
                response = requests.get(img_input)
                image = Image.open(BytesIO(response.content))

            # Save temporarily to disk (engine.py works with file paths)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_path = tmp.name
                image.save(tmp_path)

            try:
                model = engine.load_model(ctx_id=-1)
                img_cv = cv2.imread(tmp_path)
                faces = model.get(img_cv)

                embeddings = []
                for i, face in enumerate(faces):
                    print(f"  Face {i+1}/{len(faces)} in image {idx+1}")
                    embeddings.append({
                        "vector": face.embedding.tolist(),
                        "confidence": float(face.det_score),
                        "bbox": face.bbox.tolist()
                    })

                all_results.append({
                    "image_index": idx,
                    "num_faces": len(faces),
                    "embeddings": embeddings
                })

            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            print(f"Error processing image {idx+1}: {e}")
            all_results.append({
                "image_index": idx,
                "num_faces": 0,
                "embeddings": [],
                "error": str(e)
            })

    print("All images processed.")
    return {"results": all_results}

@app.post("/api/search-faces")
async def search_faces(reference_embedding: List[float], threshold: float = 0.6):
    """
    Search for similar faces using FAISS index from engine.py
    """
    try:
        embeddings_array, image_paths, num_faces_per_image, output_folder = engine.load_embeddings()
        if embeddings_array.size == 0:
            return {"matches": []}

        index = engine.build_faiss_index(embeddings_array)
        reference_emb = np.array([reference_embedding]).astype('float32')
        k = min(10, len(embeddings_array))
        distances, indices = index.search(reference_emb, k)

        matches = []
        for i, idx in enumerate(indices[0]):
            distance = float(distances[0][i])
            similarity = 1 / (1 + distance)
            if similarity > threshold:
                matches.append({
                    "photo_path": image_paths[idx],
                    "similarity": similarity,
                    "distance": distance
                })

        return {"matches": matches}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No embeddings found. Please build embeddings first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
