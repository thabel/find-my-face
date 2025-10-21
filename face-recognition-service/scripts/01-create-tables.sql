-- Create events table for storing event information
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  event_date DATE NOT NULL,
  created_by TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived'))
);

-- Create photos table for storing uploaded photos
CREATE TABLE IF NOT EXISTS photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  file_name TEXT NOT NULL,
  uploaded_by TEXT NOT NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed BOOLEAN DEFAULT FALSE
);

-- Create face_embeddings table for storing face recognition data
CREATE TABLE IF NOT EXISTS face_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
  embedding VECTOR(512),
  bbox JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_photos_event_id ON photos(event_id);
CREATE INDEX IF NOT EXISTS idx_face_embeddings_photo_id ON face_embeddings(photo_id);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);

-- Enable Row Level Security
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE face_embeddings ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (you can customize these later)
CREATE POLICY "Allow public read access to events" ON events
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert to events" ON events
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to photos" ON photos
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert to photos" ON photos
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to face_embeddings" ON face_embeddings
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert to face_embeddings" ON face_embeddings
  FOR INSERT WITH CHECK (true);
