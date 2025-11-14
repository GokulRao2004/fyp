# Supabase Setup Guide for FYP Presentation Generator

## Overview
Supabase is an open-source Firebase alternative that provides:
- **PostgreSQL Database** (instead of Firestore)
- **Object Storage** (for files/images - not base64)
- **Authentication** (built-in user management)
- **Real-time** capabilities

## Step 1: Create Supabase Project

### 1.1 Sign Up / Log In
1. Go to https://supabase.com
2. Click "Start your project for free"
3. Sign up with email or GitHub
4. Create an organization

### 1.2 Create a New Project
1. Click "New Project"
2. Fill in:
   - **Project Name**: `fyp-ppt-generator` (or similar)
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Select closest to your location
3. Click "Create new project" (takes 2-3 minutes)

### 1.3 Get Your Credentials
After project creation, go to **Settings > API**:
- **Project URL**: Copy this (e.g., `https://xxxx.supabase.co`)
- **Anon Key**: Copy this (public key for client)
- **Service Role Key**: Copy this (secret key for backend)

**⚠️ IMPORTANT: Never commit these keys to git!**

---

## Step 2: Setup Environment Variables

Create `.env` file in `BE/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Optional
SUPABASE_JWT_SECRET=your-jwt-secret
```

Update `requirements.txt`:
```
supabase==2.0.3
python-dotenv==1.0.0
```

---

## Step 3: Create Database Tables

### 3.1 Open Supabase SQL Editor
1. In Supabase Dashboard, go to **SQL Editor**
2. Click "New query"

### 3.2 Create Tables - Run These SQL Queries

#### Table 1: Users (Extended Profile)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT NOT NULL,
  display_name TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own data" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
  FOR UPDATE USING (auth.uid() = id);
```

#### Table 2: Presentations
```sql
CREATE TABLE presentations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  ppt_id TEXT UNIQUE NOT NULL,
  topic TEXT NOT NULL,
  theme TEXT DEFAULT 'modern',
  slide_count INTEGER DEFAULT 0,
  content_sources TEXT[] DEFAULT ARRAY[]::TEXT[],
  brand_colors JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE presentations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own presentations" ON presentations
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create presentations" ON presentations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own presentations" ON presentations
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own presentations" ON presentations
  FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX presentations_user_id_idx ON presentations(user_id);
CREATE INDEX presentations_created_at_idx ON presentations(created_at DESC);
```

#### Table 3: Slides
```sql
CREATE TABLE slides (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  presentation_id UUID NOT NULL REFERENCES presentations(id) ON DELETE CASCADE,
  slide_index INTEGER NOT NULL,
  title TEXT,
  content TEXT,
  image_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE slides ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read slides of their presentations" ON slides
  FOR SELECT USING (
    presentation_id IN (
      SELECT id FROM presentations WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create slides in their presentations" ON slides
  FOR INSERT WITH CHECK (
    presentation_id IN (
      SELECT id FROM presentations WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update slides in their presentations" ON slides
  FOR UPDATE USING (
    presentation_id IN (
      SELECT id FROM presentations WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete slides in their presentations" ON slides
  FOR DELETE USING (
    presentation_id IN (
      SELECT id FROM presentations WHERE user_id = auth.uid()
    )
  );

CREATE INDEX slides_presentation_id_idx ON slides(presentation_id);
```

---

## Step 4: Setup Storage Bucket

### 4.1 Create Storage Bucket
1. In Supabase Dashboard, go to **Storage**
2. Click "Create a new bucket"
3. Fill in:
   - **Name**: `presentation-images`
   - **Privacy**: Select "Private" for security
4. Click "Create bucket"

### 4.2 Create Storage Policies
Go to **Storage > Policies** for `presentation-images` bucket:

```sql
-- Allow users to upload images
CREATE POLICY "Users can upload images" ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (bucket_id = 'presentation-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow users to read their own images
CREATE POLICY "Users can read their own images" ON storage.objects
  FOR SELECT TO authenticated
  USING (bucket_id = 'presentation-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow users to delete their own images
CREATE POLICY "Users can delete their own images" ON storage.objects
  FOR DELETE TO authenticated
  USING (bucket_id = 'presentation-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

---

## Step 5: Install Python Dependencies

```bash
cd BE
pip install -r requirements.txt
```

### requirements.txt additions:
```
supabase==2.0.3
python-dotenv==1.0.0
requests==2.31.0
```

---

## Step 6: File Structure

```
BE/
├── .env (CREATE THIS - DO NOT COMMIT)
├── requirements.txt
├── app.py
├── auth.py
├── services/
│   └── supabase_service.py (REPLACES firebase_service.py)
├── api/
│   ├── generate.py
│   ├── history.py
│   └── ... (other APIs)
```

---

## Step 7: Environment Variables Summary

| Variable | Where to Find | Description |
|----------|--------------|-------------|
| `SUPABASE_URL` | Settings > API | Your project URL |
| `SUPABASE_ANON_KEY` | Settings > API | Public key (safe for frontend) |
| `SUPABASE_SERVICE_ROLE_KEY` | Settings > API | Secret key (only for backend) |

---

## Step 8: Testing Connection

Create `test_supabase_init.py`:

```python
from services.supabase_service import supabase_service
import logging

logging.basicConfig(level=logging.INFO)

try:
    # Test connection
    result = supabase_service.test_connection()
    if result:
        print("✅ Supabase connection successful!")
    else:
        print("❌ Supabase connection failed!")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run: `python test_supabase_init.py`

---

## Key Differences from Firebase

| Feature | Firebase | Supabase |
|---------|----------|----------|
| Database | Firestore (NoSQL) | PostgreSQL (SQL) |
| Images | Cloud Storage (separate) | Object Storage (in bucket) |
| Base64 | Not needed | Not needed |
| Auth | Firebase Auth | Supabase Auth |
| Access Control | Firestore Rules | Row Level Security (RLS) |
| Cost | Pay per read/write | Pay per GB + compute |

---

## Useful Links

- **Supabase Dashboard**: https://app.supabase.com
- **Python SDK Docs**: https://supabase.com/docs/reference/python/introduction
- **Storage Guide**: https://supabase.com/docs/guides/storage
- **Database Guide**: https://supabase.com/docs/guides/database/overview
- **Row Level Security**: https://supabase.com/docs/guides/auth/row-level-security

---

## Troubleshooting

### Connection Error
- Check `.env` file exists and has correct keys
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`

### Storage Upload Error
- Ensure bucket is created and policies are set
- Check folder path follows format: `user_id/presentation_id/filename`

### Authentication Error
- Ensure `users` table exists
- Check Row Level Security policies

### Database Error
- Verify tables exist via SQL Editor
- Check policies are enabled

---

## Migration from Firebase to Supabase (Optional)

Use this command to migrate existing Firestore data:
```bash
supabase db push  # After creating migrations
```

---

**Need Help?** Join Supabase Discord: https://discord.supabase.com
