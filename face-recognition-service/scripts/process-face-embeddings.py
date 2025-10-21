"""
Script to process uploaded photos and extract face embeddings using InsightFace.
This script should be run after photos are uploaded to process them.
"""

import os
import numpy as np
from insightface.app import FaceAnalysis
from supabase import create_client, Client
import json

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize InsightFace
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

def process_photo(photo_id: str, image_path: str):
    """
    Process a single photo to extract face embeddings.
    
    Args:
        photo_id: UUID of the photo in the database
        image_path: Path or URL to the image file
    """
    try:
        # Load image
        import cv2
        import urllib.request
        
        # Download image if it's a URL
        if image_path.startswith('http'):
            req = urllib.request.urlopen(image_path)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
        else:
            img = cv2.imread(image_path)
        
        # Detect faces
        faces = app.get(img)
        
        print(f"Found {len(faces)} face(s) in photo {photo_id}")
        
        # Store each face embedding
        for face in faces:
            embedding = face.embedding.tolist()
            bbox = {
                'x': float(face.bbox[0]),
                'y': float(face.bbox[1]),
                'width': float(face.bbox[2] - face.bbox[0]),
                'height': float(face.bbox[3] - face.bbox[1])
            }
            
            # Insert into database
            supabase.table('face_embeddings').insert({
                'photo_id': photo_id,
                'embedding': embedding,
                'bbox': json.dumps(bbox)
            }).execute()
        
        # Mark photo as processed
        supabase.table('photos').update({
            'processed': True
        }).eq('id', photo_id).execute()
        
        return len(faces)
        
    except Exception as e:
        print(f"Error processing photo {photo_id}: {str(e)}")
        return 0

def process_unprocessed_photos():
    """
    Process all unprocessed photos in the database.
    """
    # Get unprocessed photos
    response = supabase.table('photos').select('*').eq('processed', False).execute()
    photos = response.data
    
    print(f"Found {len(photos)} unprocessed photo(s)")
    
    total_faces = 0
    for photo in photos:
        faces_count = process_photo(photo['id'], photo['file_path'])
        total_faces += faces_count
    
    print(f"Processing complete! Extracted {total_faces} face(s) from {len(photos)} photo(s)")

if __name__ == "__main__":
    process_unprocessed_photos()
