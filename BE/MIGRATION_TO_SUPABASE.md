# Firebase to Supabase Migration Guide

This document provides step-by-step instructions for migrating the application from Firebase to Supabase.

## Overview of Changes

| Component | Firebase | Supabase |
|-----------|----------|----------|
| **Database** | Firestore (NoSQL) | PostgreSQL (SQL) |
| **Storage** | Cloud Storage + Base64 | Object Storage (files) |
| **Auth** | Firebase Auth | Supabase Auth / JWT |
| **Service File** | `services/firebase_service.py` | `services/supabase_service.py` |
| **Auth File** | `auth.py` | `auth_supabase.py` (new) |
| **Dependencies** | firebase-admin | supabase, python-dotenv |

## Setup Steps

### Step 1: Update Python Dependencies

Add to `requirements.txt`:
```
supabase==2.0.3
python-dotenv==1.0.0
PyJWT==2.8.1
```

Run:
```bash
pip install -r requirements.txt
```

### Step 2: Create `.env` File

Create `BE/.env` with your Supabase credentials (see SUPABASE_SETUP_GUIDE.md):
```
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
```

### Step 3: Update `auth.py`

**Old `auth.py`:**
- Used Firebase authentication
- Imported from `firebase_service`

**New: Use `auth_supabase.py`** (already created)

In your Flask app.py:
```python
from auth_supabase import require_auth, optional_auth, supabase_auth
```

### Step 4: Update API Files

#### `api/generate.py`

**Find and replace:**

```python
# OLD
from services.firebase_service import firebase_service
from storage import ppt_storage

# NEW
from services.supabase_service import supabase_service
```

**Update presentation save logic:**

```python
# OLD
firebase_service.create_presentation(user_id, {
    'topic': topic,
    'slides': slides_data,
    'theme': theme
})

# NEW
ppt_id = supabase_service.create_presentation(user_id, {
    'topic': topic,
    'slides': slides_data,
    'theme': theme
})
```

#### `api/history.py`

**Find and replace:**

```python
# OLD
from services.firebase_service import firebase_service

presentations = firebase_service.get_user_presentations(user_id, limit=limit)

# NEW
from services.supabase_service import supabase_service

presentations = supabase_service.get_user_presentations(user_id, limit=limit)
```

#### `api/replace_image.py`

**Find and replace:**

```python
# OLD
from storage import ppt_storage
from services.firebase_service import firebase_service

# NEW
from services.supabase_service import supabase_service
from services.pixabay import PixabayClient
```

**Update image replacement logic:**

```python
# OLD
firebase_service.update_presentation(ppt_id, user_id, {
    'slides': updated_slides
})

# NEW
supabase_service.update_presentation(ppt_id, user_id, {
    'slides': updated_slides
})
```

### Step 5: Update `services/pixabay.py`

Add method to upload and store images in Supabase:

```python
# Add this to PixabayClient class

def save_image_to_supabase(self, image_url: str, destination_path: str):
    """
    Download image from Pixabay and save to Supabase storage
    
    Args:
        image_url: URL of image from Pixabay
        destination_path: Where to save in Supabase storage (e.g., "presentations/ppt_id/slide_1.jpg")
        
    Returns:
        Public URL of stored image
    """
    try:
        from services.supabase_service import supabase_service
        
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Upload to Supabase
        public_url = supabase_service.upload_image(
            response.content,
            destination_path,
            content_type=response.headers.get('content-type', 'image/jpeg')
        )
        
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to save image to Supabase: {e}")
        raise
```

## API Method Mappings

### Presentations

```python
# OLD Firebase → NEW Supabase

# Create
firebase_service.create_presentation(user_id, data)
→ supabase_service.create_presentation(user_id, data)

# Get
firebase_service.get_presentation(ppt_id, user_id)
→ supabase_service.get_presentation(ppt_id, user_id)

# Update
firebase_service.update_presentation(ppt_id, user_id, updates)
→ supabase_service.update_presentation(ppt_id, user_id, updates)

# Delete
firebase_service.delete_presentation(ppt_id, user_id)
→ supabase_service.delete_presentation(ppt_id, user_id)

# List user presentations
firebase_service.get_user_presentations(user_id, limit)
→ supabase_service.get_user_presentations(user_id, limit)
```

### Slides

```python
# Add slide
firebase_service.add_slide(ppt_id, user_id, slide_data)
→ supabase_service.add_slide_to_presentation(ppt_id, user_id, slide_data)

# Delete slide
firebase_service.delete_slide(ppt_id, user_id, slide_index)
→ supabase_service.delete_slide_from_presentation(ppt_id, user_id, slide_index)

# Get slides
firebase_service.get_slides(ppt_id, user_id)
→ supabase_service.get_slides(ppt_id, user_id)
```

### Images

```python
# Upload image
firebase_service.upload_image(image_bytes, path, content_type)
→ supabase_service.upload_image(image_bytes, path, content_type)

# Download image
firebase_service.download_image(path)
→ supabase_service.download_image(path)

# Delete image
firebase_service.delete_image(path)
→ supabase_service.delete_image(path)

# Get public URL
firebase_service.get_public_url(path)
→ supabase_service.get_public_url(path)
```

## Important Differences

### 1. User Context
- **Firebase**: Could work with user ID from Firestore directly
- **Supabase**: Requires user_id from JWT token or application state
- **Action**: Always pass `user_id` explicitly to methods

### 2. Authorization
- **Firebase**: Firestore RLS (Rules)
- **Supabase**: PostgreSQL RLS policies (SQL)
- **Action**: Only your backend service role key can bypass RLS for admin operations

### 3. Image Storage
- **Firebase**: Stored as base64 in Firestore documents
- **Supabase**: Stored as files in Object Storage bucket
- **Action**: Use `supabase_service.upload_image()` for files, not base64

### 4. Data Relationships
- **Firebase**: Document references
- **Supabase**: Foreign keys (SQL)
- **Action**: RLS policies automatically enforce data isolation

### 5. Error Handling
- **Firebase**: Custom error types
- **Supabase**: Standard exceptions with `.error` attribute
- **Action**: Catch generic `Exception` and check `.error` for details

## Testing the Migration

### 1. Test Supabase Connection
```bash
cd BE
python -c "from services.supabase_service import supabase_service; print('✅ Supabase connected!' if supabase_service else '❌ Failed')"
```

### 2. Test Image Upload
```python
from services.supabase_service import supabase_service

# Upload test image
test_image = b"fake image data"
url = supabase_service.upload_image(
    test_image,
    "test/test_image.jpg",
    "image/jpeg"
)
print(f"✅ Uploaded: {url}")

# Download and verify
downloaded = supabase_service.download_image("test/test_image.jpg")
print(f"✅ Downloaded: {len(downloaded)} bytes")

# Cleanup
supabase_service.delete_image("test/test_image.jpg")
print("✅ Deleted")
```

### 3. Test Presentation CRUD
```python
from services.supabase_service import supabase_service
import uuid

user_id = str(uuid.uuid4())

# Create user
supabase_service.create_user(user_id, "test@example.com", "Test User")

# Create presentation
ppt_id = supabase_service.create_presentation(user_id, {
    "topic": "Test",
    "theme": "modern",
    "slide_count": 1
})
print(f"✅ Created: {ppt_id}")

# Get presentation
ppt = supabase_service.get_presentation(ppt_id, user_id)
print(f"✅ Retrieved: {ppt['topic']}")

# Update presentation
supabase_service.update_presentation(ppt_id, user_id, {
    "topic": "Updated Test"
})
print("✅ Updated")

# Delete presentation
supabase_service.delete_presentation(ppt_id, user_id)
print("✅ Deleted")
```

## Rollback Plan (Keep Firebase Running Parallel)

If you want to run both systems in parallel during testing:

1. Create a new service file `services/database_selector.py`:
```python
import os

def get_database_service():
    """Select database service based on environment"""
    if os.getenv('USE_SUPABASE', 'false').lower() == 'true':
        from services.supabase_service import supabase_service
        return supabase_service
    else:
        from services.firebase_service import firebase_service
        return firebase_service
```

2. Update API files to use selector:
```python
from services.database_selector import get_database_service

db_service = get_database_service()
```

3. In `.env`, toggle between systems:
```
USE_SUPABASE=true   # Switch to Supabase
USE_SUPABASE=false  # Switch to Firebase
```

## Troubleshooting

### "SUPABASE_URL not found in environment"
- ✅ Solution: Check `.env` file exists in `BE/` directory
- ✅ Solution: Run `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('SUPABASE_URL'))"`

### "Permission denied" on image upload
- ✅ Solution: Check storage bucket RLS policies are enabled (see SUPABASE_SETUP_GUIDE.md Step 4)
- ✅ Solution: Check service role key in `.env` is correct

### "Relation 'presentations' does not exist"
- ✅ Solution: Database tables not created yet
- ✅ Solution: Run SQL migrations from SUPABASE_SETUP_GUIDE.md Step 3

### Connection timeout
- ✅ Solution: Check SUPABASE_URL is correct format: `https://[project-id].supabase.co`
- ✅ Solution: Check firewall allows outbound HTTPS (port 443)
- ✅ Solution: Try: `curl -I https://[project-id].supabase.co`

## Cleanup

Once migration is complete and tested:

1. Delete old Firebase files:
```bash
rm BE/services/firebase_service.py
rm BE/auth.py  # (kept as backup, but use auth_supabase.py)
rm BE/storage.py
rm BE/service-key.json  # Firebase credentials - no longer needed
```

2. Update `.gitignore`:
```
# Add if not present
.env
*.local
service-key.json
```

3. Update documentation:
- Update STARTUP_GUIDE.md to reference Supabase setup
- Remove Firebase references from README.md files

## Migration Checklist

- [ ] Create Supabase project and get credentials
- [ ] Create .env file with Supabase credentials
- [ ] Run SQL migrations to create tables
- [ ] Create storage bucket and set RLS policies
- [ ] Update requirements.txt with new dependencies
- [ ] Update auth.py imports to use auth_supabase.py
- [ ] Update api/generate.py imports
- [ ] Update api/history.py imports
- [ ] Update api/replace_image.py imports
- [ ] Update services/pixabay.py to use supabase_service
- [ ] Test Supabase connection
- [ ] Test image upload/download
- [ ] Test presentation CRUD operations
- [ ] Test authentication flow
- [ ] Delete old Firebase service files (after verification)
- [ ] Update startup documentation

## Support

For Supabase documentation, see: https://supabase.com/docs
For issues, check: SUPABASE_SETUP_GUIDE.md Troubleshooting section
