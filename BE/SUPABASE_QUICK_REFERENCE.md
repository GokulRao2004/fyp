# Supabase Implementation - Quick Reference

## 📋 Files Created/Modified

### ✅ NEW FILES
- `BE/services/supabase_service.py` - Main Supabase service (580+ lines)
- `BE/auth_supabase.py` - Supabase authentication decorators
- `SUPABASE_SETUP_GUIDE.md` - Comprehensive setup with SQL queries
- `MIGRATION_TO_SUPABASE.md` - Step-by-step migration guide
- `test_supabase_init.py` - Test suite for verification
- `SUPABASE_MIGRATION_COMPLETE.md` - This comprehensive guide

### ✏️ MODIFIED FILES
- `BE/requirements.txt` - Updated dependencies (removed firebase-admin, added supabase)

### ❌ TO DELETE (After Testing)
- `BE/services/firebase_service.py`
- `BE/auth.py` (use auth_supabase.py instead)
- `BE/storage.py`
- `BE/service-key.json`

---

## 🚀 Quick Start (5 Steps)

### 1️⃣ CREATE SUPABASE PROJECT (5 min)
```
→ Go to supabase.com
→ Create new project
→ Get credentials from Settings > API:
  • SUPABASE_URL
  • SUPABASE_SERVICE_ROLE_KEY
  • SUPABASE_ANON_KEY
  • SUPABASE_JWT_SECRET
```

### 2️⃣ CREATE .env FILE (1 min)
```bash
# Create BE/.env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=super-secret-key
```

### 3️⃣ RUN DATABASE MIGRATIONS (5 min)
```
→ Supabase dashboard > SQL Editor
→ Create new query
→ Paste SQL from SUPABASE_SETUP_GUIDE.md Step 3
→ Execute
```

### 4️⃣ CREATE STORAGE BUCKET (2 min)
```
→ Supabase dashboard > Storage
→ Create bucket "presentation-images"
→ Set to PRIVATE
→ Apply RLS policies from SUPABASE_SETUP_GUIDE.md Step 4
```

### 5️⃣ INSTALL & TEST (3 min)
```bash
cd BE
pip install -r requirements.txt
python test_supabase_init.py  # Should show ✅ ALL TESTS PASSED!
```

---

## 📚 API REFERENCE

### Import in Your Code
```python
from services.supabase_service import supabase_service
```

### Image Operations
```python
# Upload image
url = supabase_service.upload_image(
    image_bytes,
    "presentations/ppt_id/slide_1.jpg",
    "image/jpeg"
)

# Download image
image_bytes = supabase_service.download_image("presentations/ppt_id/slide_1.jpg")

# Delete image
supabase_service.delete_image("presentations/ppt_id/slide_1.jpg")

# Get public URL
public_url = supabase_service.get_public_url("presentations/ppt_id/slide_1.jpg")
```

### Presentation Operations
```python
# Create presentation
ppt_id = supabase_service.create_presentation(user_id, {
    'topic': 'My Presentation',
    'theme': 'modern',
    'slide_count': 3,
    'num_slides': 3
})

# Get presentation
ppt = supabase_service.get_presentation(ppt_id, user_id)

# Update presentation
supabase_service.update_presentation(ppt_id, user_id, {
    'topic': 'Updated Title'
})

# Delete presentation (also deletes slides and images)
supabase_service.delete_presentation(ppt_id, user_id)

# List user's presentations
presentations = supabase_service.get_user_presentations(user_id, limit=50)
```

### Slide Operations
```python
# Add slide
supabase_service.add_slide_to_presentation(ppt_id, user_id, {
    'title': 'Slide Title',
    'content': 'Slide content',
    'layout': 'title_content',
    'notes': 'Speaker notes'
})

# Get all slides
slides = supabase_service.get_slides(ppt_id, user_id)

# Delete slide
supabase_service.delete_slide_from_presentation(ppt_id, user_id, 0)
```

### User Operations
```python
# Create user
supabase_service.create_user(user_id, "email@example.com", "Display Name")

# Get user
user = supabase_service.get_user(user_id)
```

### Authentication
```python
from auth_supabase import require_auth, optional_auth

@app.route('/my-route', methods=['POST'])
@require_auth
def my_endpoint():
    user_id = request.user_id
    user_email = request.user_email
    user_info = request.user_info
    # ...
```

---

## 🔄 Firebase → Supabase Import Changes

### Old (Firebase)
```python
from services.firebase_service import firebase_service
```

### New (Supabase)
```python
from services.supabase_service import supabase_service
```

### Old (Auth)
```python
from auth import require_auth, optional_auth
```

### New (Auth)
```python
from auth_supabase import require_auth, optional_auth, supabase_auth
```

---

## 🧪 Running Tests

```bash
cd BE
python test_supabase_init.py
```

Expected output:
```
✅ Connection tests passed
✅ User tests passed
✅ Presentation CRUD tests passed
✅ Slide operations tests passed
✅ Image storage tests passed

🎉 ALL TESTS PASSED!
```

---

## 🔐 Environment Variables

| Variable | Where to Find | Used For |
|----------|--------------|----------|
| `SUPABASE_URL` | Settings > API > URL | Database connection |
| `SUPABASE_SERVICE_ROLE_KEY` | Settings > API > Service role key | Backend operations |
| `SUPABASE_ANON_KEY` | Settings > API > Anon key | Client-side operations |
| `SUPABASE_JWT_SECRET` | Settings > API > JWT Secret | Token verification |
| `PIXABAY_API_KEY` | (existing) | Image search |

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `SUPABASE_URL not found` | Create `.env` in `BE/` directory |
| `Permission denied` on upload | Check storage bucket RLS policies |
| `Relation 'presentations' does not exist` | Run SQL migration (Step 3) |
| `Connection refused` | Check firewall allows port 443 |
| `Invalid token` | Check `SUPABASE_SERVICE_ROLE_KEY` is correct |
| `Storage bucket not found` | Create `presentation-images` bucket as PRIVATE |

---

## 📊 Database Schema

### users
```sql
id (UUID) PRIMARY KEY
email (TEXT) UNIQUE
display_name (TEXT)
created_at (TIMESTAMP)
```

### presentations
```sql
id (UUID) PRIMARY KEY
user_id (UUID) FOREIGN KEY → users
topic (TEXT)
theme (TEXT)
slide_count (INT)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### slides
```sql
id (UUID) PRIMARY KEY
presentation_id (UUID) FOREIGN KEY → presentations
slide_index (INT)
title (TEXT)
content (TEXT)
layout (TEXT)
notes (TEXT)
created_at (TIMESTAMP)
```

---

## 📁 Project Structure

```
BE/
├── services/
│   ├── supabase_service.py      ← NEW: Main service
│   ├── pixabay.py               ← UPDATE: Add new method
│   ├── ppt_service.py           ← No change
│   └── ...
├── api/
│   ├── generate.py              ← UPDATE: Change imports
│   ├── history.py               ← UPDATE: Change imports
│   ├── replace_image.py         ← UPDATE: Change imports
│   └── ...
├── auth_supabase.py             ← NEW: Auth decorators
├── app.py                       ← UPDATE: Import auth_supabase
├── requirements.txt             ← ✅ UPDATED
├── .env                         ← NEW: Create with credentials
├── test_supabase_init.py        ← NEW: Test suite
├── SUPABASE_SETUP_GUIDE.md      ← NEW: Setup instructions
├── MIGRATION_TO_SUPABASE.md     ← NEW: Migration guide
└── SUPABASE_MIGRATION_COMPLETE.md ← NEW: This document
```

---

## ✅ Migration Checklist

- [ ] Supabase project created
- [ ] Credentials retrieved
- [ ] `.env` file created in `BE/`
- [ ] `.env` added to `.gitignore`
- [ ] SQL migrations executed
- [ ] Storage bucket created with RLS policies
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`python test_supabase_init.py`)
- [ ] `api/generate.py` imports updated
- [ ] `api/history.py` imports updated
- [ ] `api/replace_image.py` imports updated
- [ ] `services/pixabay.py` updated with new method
- [ ] `app.py` auth imports updated
- [ ] Full application tested
- [ ] Old Firebase files deleted (optional)

---

## 🔗 Useful Links

- **Supabase Docs**: https://supabase.com/docs
- **Python SDK**: https://github.com/supabase/supabase-py
- **Setup Guide**: `SUPABASE_SETUP_GUIDE.md`
- **Migration Guide**: `MIGRATION_TO_SUPABASE.md`
- **Complete Guide**: `SUPABASE_MIGRATION_COMPLETE.md`

---

## 💡 Tips & Best Practices

1. **Always use service role key on backend only**
   ```python
   # ✅ GOOD - Backend only
   supabase_service.create_presentation(user_id, data)
   
   # ❌ WRONG - Don't expose to client
   return SUPABASE_SERVICE_ROLE_KEY
   ```

2. **Always pass user_id explicitly**
   ```python
   # ✅ GOOD
   supabase_service.get_presentation(ppt_id, user_id)
   
   # ❌ WRONG - Missing user_id
   supabase_service.get_presentation(ppt_id)
   ```

3. **Images are files, not base64**
   ```python
   # ✅ GOOD - Upload as file
   url = supabase_service.upload_image(image_bytes, "path/file.jpg")
   
   # ❌ WRONG - Don't store base64 in database
   db.save({'thumbnail': 'data:image/jpeg;base64,...'})
   ```

4. **Handle exceptions properly**
   ```python
   # ✅ GOOD - Catch and log
   try:
       supabase_service.upload_image(...)
   except Exception as e:
       logger.error(f"Upload failed: {e}")
       return error_response(500)
   
   # ❌ WRONG - Silent failures
   supabase_service.upload_image(...)
   ```

---

## 📞 Support

Need help? Check:
1. `SUPABASE_MIGRATION_COMPLETE.md` - Full documentation
2. `SUPABASE_SETUP_GUIDE.md` - Setup and troubleshooting
3. `MIGRATION_TO_SUPABASE.md` - API mapping and examples
4. `test_supabase_init.py` - Working code examples

---

**Last Updated**: [Date of migration completion]
**Status**: ✅ Ready for deployment
**Next Step**: Follow Quick Start section above!
