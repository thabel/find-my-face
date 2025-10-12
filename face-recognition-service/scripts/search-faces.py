"""
Script to search for matching faces given a reference photo.
This uses cosine similarity to find similar face embeddings.
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

def cosine_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings."""
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def extract_reference_embedding(image_path: str):
    """
    Extract face embedding from a reference photo.
    
    Args:
        image_path: Path or URL to the reference image
        
    Returns:
        Face embedding as numpy array, or None if no face found
    """
    try:
        import cv2
        import urllib.request
        
        # Load image
        if image_path.startswith('http'):
            req = urllib.request.urlopen(image_path)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
        else:
            img = cv2.imread(image_path)
        
        # Detect faces
        faces = app.get(img)
        
        if len(faces) == 0:
            print("No face detected in reference image")
            return None
        
        if len(faces) > 1:
            print(f"Warning: Multiple faces detected ({len(faces)}), using the first one")
        
        return faces[0].embedding
        
    except Exception as e:
        print(f"Error extracting reference embedding: {str(e)}")
        return None

def search_similar_faces(reference_embedding, threshold=0.6, event_id=None):
    """
    Search for photos containing similar faces.
    
    Args:
        reference_embedding: Face embedding to search for
        threshold: Similarity threshold (0-1, higher = more strict)
        event_id: Optional event ID to filter results
        
    Returns:
        List of matching photo IDs with similarity scores
    """
    try:
        # Get all face embeddings from database
        query = supabase.table('face_embeddings').select('id, photo_id, embedding')
        
        if event_id:
            # Join with photos table to filter by event
            query = query.join('photos', 'photo_id').eq('photos.event_id', event_id)
        
        response = query.execute()
        embeddings = response.data
        
        print(f"Comparing against {len(embeddings)} face embedding(s)")
        
        matches = []
        for item in embeddings:
            stored_embedding = item['embedding']
            similarity = cosine_similarity(reference_embedding, stored_embedding)
            
            if similarity >= threshold:
                matches.append({
                    'photo_id': item['photo_id'],
                    'similarity': float(similarity)
                })
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Get unique photo IDs
        unique_photos = {}
        for match in matches:
            photo_id = match['photo_id']
            if photo_id not in unique_photos or match['similarity'] > unique_photos[photo_id]:
                unique_photos[photo_id] = match['similarity']
        
        result = [{'photo_id': pid, 'similarity': sim} for pid, sim in unique_photos.items()]
        
        print(f"Found {len(result)} matching photo(s)")
        return result
        
    except Exception as e:
        print(f"Error searching faces: {str(e)}")
        return []

def get_photo_urls(photo_ids):
    """Get the URLs for a list of photo IDs."""
    if not photo_ids:
        return []
    
    response = supabase.table('photos').select('id, file_path, file_name').in_('id', photo_ids).execute()
    return response.data

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python search-faces.py <reference_image_path> [threshold] [event_id]")
        sys.exit(1)
    
    reference_path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
    event_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Extract reference embedding
    ref_embedding = extract_reference_embedding(reference_path)
    
    if ref_embedding is not None:
        # Search for matches
        matches = search_similar_faces(ref_embedding, threshold, event_id)
        
        # Get photo URLs
        photo_ids = [m['photo_id'] for m in matches]
        photos = get_photo_urls(photo_ids)
        
        print("\nMatching photos:")
        for photo in photos:
            match = next(m for m in matches if m['photo_id'] == photo['id'])
            print(f"- {photo['file_name']} (similarity: {match['similarity']:.2%})")
