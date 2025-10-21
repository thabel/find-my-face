# Deployment Guide

This guide explains how to deploy your Face Recognition Service.

## Architecture Overview

\`\`\`
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Next.js App   │────────▶│  Python FastAPI  │────────▶│  Supabase   │
│   (Vercel)      │         │  (Railway/VPS)   │         │  (Database) │
└─────────────────┘         └──────────────────┘         └─────────────┘
\`\`\`

## Quick Setup: Environment Variables

### For Next.js Frontend (Vercel)

Add these environment variables in your Vercel project settings:

| Variable | Value | Example |
|----------|-------|---------|
| `PYTHON_API_URL` | Your Python backend URL | `https://your-app.railway.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ Already configured | - |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ Already configured | - |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Already configured | - |

### Python API URL Examples

Choose based on where you deploy the Python backend:

**Local Development:**
\`\`\`
PYTHON_API_URL=http://localhost:8000
\`\`\`

**Railway (Recommended):**
\`\`\`
PYTHON_API_URL=https://face-recognition-production.up.railway.app
\`\`\`

**DigitalOcean:**
\`\`\`
PYTHON_API_URL=https://164.92.xxx.xxx:8000
\`\`\`

**AWS EC2:**
\`\`\`
PYTHON_API_URL=https://ec2-xx-xxx-xxx-xx.compute-1.amazonaws.com:8000
\`\`\`

**Custom Domain:**
\`\`\`
PYTHON_API_URL=https://api.yourapp.com
\`\`\`

## Step 1: Deploy Database (Supabase)

✅ Already configured! Your Supabase database is ready.

Run the SQL script to create tables:
- Go to Supabase Dashboard → SQL Editor
- Run `scripts/01-create-tables.sql`

## Step 2: Deploy Python Backend

### Option A: Railway (Easiest) ⭐ Recommended

1. **Create Railway Account**: Go to [railway.app](https://railway.app)

2. **Create New Project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository
   - Choose the `python-backend` directory as root

3. **Configure Build**:
   - Railway auto-detects Python from `requirements.txt`
   - No additional configuration needed

4. **Add Environment Variables** (if needed):
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase service role key

5. **Deploy**: 
   - Railway automatically deploys on push
   - Wait for build to complete (~2-3 minutes)

6. **Get Your API URL**:
   - Go to Settings → Domains
   - Railway provides a URL like: `https://face-recognition-production.up.railway.app`
   - **Copy this URL** - you'll need it for the Next.js frontend

7. **Test Your API**:
\`\`\`bash
curl https://your-app.railway.app/
# Should return: {"status": "Face Recognition API is running"}
\`\`\`

**Cost**: ~$5/month with Railway's usage-based pricing

### Option B: DigitalOcean Droplet

1. Create a Droplet (Ubuntu 22.04, 2GB RAM minimum)
2. SSH into your droplet
3. Install dependencies:
\`\`\`bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
\`\`\`

4. Clone your code and setup:
\`\`\`bash
cd /var/www
git clone your-repo
cd your-repo/python-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

5. Create systemd service:
\`\`\`bash
sudo nano /etc/systemd/system/facerecognition.service
\`\`\`

Add:
\`\`\`ini
[Unit]
Description=Face Recognition API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/your-repo/python-backend
Environment="PATH=/var/www/your-repo/python-backend/venv/bin"
ExecStart=/var/www/your-repo/python-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
\`\`\`

6. Start service:
\`\`\`bash
sudo systemctl start facerecognition
sudo systemctl enable facerecognition
\`\`\`

7. Configure Nginx as reverse proxy

## Step 3: Deploy Next.js Frontend (Vercel)

1. **Push to GitHub**: Ensure your code is on GitHub

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel auto-detects Next.js

3. **Add Environment Variables**:
   
   **Required - Add this:**
   - `PYTHON_API_URL`: Your Python backend URL from Step 2
     - Example: `https://face-recognition-production.up.railway.app`
   
   **Already configured ✅:**
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

4. **Deploy**: Click "Deploy"

5. **Done!** Your app is live at `https://your-app.vercel.app`

## Step 4: Configure Storage

1. Go to Supabase Dashboard → Storage
2. Create a new bucket called `event-photos`
3. Set bucket to **public** (or configure RLS policies)

## Testing

1. **Test Python API**:
\`\`\`bash
curl https://your-python-backend.com/
# Should return: {"status": "Face Recognition API is running"}
\`\`\`

2. **Test Frontend**:
   - Visit your Vercel URL
   - Try creating an event as Producer
   - Try uploading photos
   - Try searching as Consumer

## Troubleshooting

### Python API not responding
- Check Railway/server logs
- Ensure port 8000 is open
- Verify InsightFace models downloaded

### Photos not uploading
- Check Supabase Storage bucket is public
- Verify CORS settings in Supabase

### Face recognition not working
- Ensure `PYTHON_API_URL` is set correctly in Vercel
- Check Python API logs for errors
- Verify image URLs are accessible

## Cost Estimates

- **Supabase**: Free tier (500MB database, 1GB storage)
- **Railway**: ~$5-10/month (with usage-based pricing)
- **Vercel**: Free tier (hobby projects)

**Total**: ~$5-10/month for small to medium usage

## Scaling Considerations

For high-traffic events:
- Upgrade Railway to larger instance
- Use Supabase Pro for better performance
- Consider CDN for image delivery
- Implement Redis caching for embeddings
