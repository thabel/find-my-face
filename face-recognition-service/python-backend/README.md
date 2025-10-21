# Face Recognition Backend (Python FastAPI)

This is the Python backend service that handles face recognition using InsightFace.

## Architecture

- **Frontend (Next.js)**: Deployed on Vercel - handles UI and user interactions
- **Backend (FastAPI)**: Deployed separately - handles face recognition with InsightFace
- **Database (Supabase)**: Stores events, photos, and face embeddings

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Install dependencies:

\`\`\`bash
pip install fastapi uvicorn insightface onnxruntime numpy pillow requests python-multipart supabase
\`\`\`

2. Download InsightFace models (first run will download automatically)

3. Run the server:

\`\`\`bash
uvicorn main:app --host 0.0.0.0 --port 8000
\`\`\`

## API Endpoints

### POST /api/extract-embeddings

Extract face embeddings from an image URL.

**Request:**
\`\`\`json
{
  "image_url": "https://example.com/photo.jpg"
}
\`\`\`

**Response:**
\`\`\`json
{
  "embeddings": [
    {
      "vector": [0.123, 0.456, ...],
      "confidence": 0.98,
      "bbox": [x1, y1, x2, y2]
    }
  ]
}
\`\`\`

### POST /api/search-faces

Search for similar faces in the database.

**Request:**
\`\`\`json
{
  "reference_embedding": [0.123, 0.456, ...],
  "threshold": 0.6,
  "event_id": "uuid"
}
\`\`\`

**Response:**
\`\`\`json
{
  "matches": [
    {
      "photo_id": "uuid",
      "similarity": 0.85
    }
  ]
}
\`\`\`

## Deployment Options

### Option 1: Railway (Recommended for beginners)

1. Create account on [Railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Railway will auto-detect Python and deploy
4. Add environment variables if needed
5. Copy the public URL

### Option 2: AWS EC2

1. Launch EC2 instance (t2.medium or larger recommended)
2. SSH into instance
3. Install Python and dependencies
4. Run with systemd or PM2
5. Configure security groups to allow port 8000

### Option 3: DigitalOcean App Platform

1. Create new app from GitHub
2. Select Python environment
3. Configure build and run commands
4. Deploy

### Option 4: Docker

\`\`\`dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
\`\`\`

## Quick Start URLs

### Development (Local)
\`\`\`bash
# Start the Python backend locally
uvicorn main:app --host 0.0.0.0 --port 8000

# Your API will be available at:
# http://localhost:8000
\`\`\`

Add to your Next.js `.env.local`:
\`\`\`
PYTHON_API_URL=http://localhost:8000
\`\`\`

### Production URLs

After deploying, your Python API URL will look like:

**Railway:**
\`\`\`
https://face-recognition-api-production.up.railway.app
\`\`\`

**DigitalOcean:**
\`\`\`
https://your-droplet-ip:8000
# or with domain:
https://api.yourapp.com
\`\`\`

**AWS EC2:**
\`\`\`
https://ec2-xx-xxx-xxx-xx.compute-amazonaws.com:8000
\`\`\`

**Render:**
\`\`\`
https://your-app.onrender.com
\`\`\`

## Environment Variables for Next.js Frontend

After deploying the Python backend, add this environment variable to your Vercel project:

\`\`\`
PYTHON_API_URL=https://your-python-backend-url.com
\`\`\`

## Database Integration

To complete the `/api/search-faces` endpoint, you need to:

1. Install Supabase Python client:
\`\`\`bash
pip install supabase
\`\`\`

2. Add database query logic to fetch stored embeddings
3. Calculate cosine similarity with reference embedding
4. Return matching photo IDs

Example:
\`\`\`python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Query embeddings
response = supabase.table("face_embeddings").select("*").execute()
embeddings = response.data

# Calculate similarities and filter
matches = []
for emb in embeddings:
    similarity = cosine_similarity(reference_emb, np.array(emb['embedding']))
    if similarity > threshold:
        matches.append({"photo_id": emb['photo_id'], "similarity": similarity})
\`\`\`

## Performance Tips

- Use GPU for faster processing: Change `providers=['CPUExecutionProvider']` to `providers=['CUDAExecutionProvider']`
- Implement caching for frequently accessed embeddings
- Use batch processing for multiple images
- Consider using a vector database (Pinecone, Weaviate) for large-scale similarity search
