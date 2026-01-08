"""
Test Supabase Setup - Verify connection, authentication, and storage
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import supabase_service


def test_supabase_connection():
    """Test basic Supabase connection"""
    print("\n=== Testing Supabase Connection ===")
    try:
        result = supabase_service.test_connection()
        if result:
            print("✅ Supabase connection successful!")
        else:
            print("❌ Supabase connection failed")
        return result
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_storage_bucket():
    """Test if storage bucket exists and is accessible"""
    print("\n=== Testing Storage Bucket ===")
    try:
        # List buckets
        buckets = supabase_service.client.storage.list_buckets()
        bucket_names = [b.name if hasattr(b, 'name') else b['name'] for b in buckets]
        print(f"Available buckets: {bucket_names}")
        
        # Check if 'fyp' bucket exists
        if 'fyp' in bucket_names:
            print("✅ Storage bucket 'fyp' exists!")
            return True
        else:
            print("❌ Storage bucket 'fyp' not found")
            print("Creating bucket 'fyp'...")
            try:
                supabase_service.client.storage.create_bucket('fyp', {'public': True})
                print("✅ Created bucket 'fyp'")
                return True
            except Exception as create_error:
                print(f"❌ Failed to create bucket: {create_error}")
                return False
    except Exception as e:
        print(f"❌ Storage error: {e}")
        return False


def test_image_upload():
    """Test image upload to storage"""
    print("\n=== Testing Image Upload ===")
    try:
        # Create a simple test image (1x1 red pixel PNG)
        test_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        test_path = "test/test_image.png"
        
        url = supabase_service.upload_image(test_image_bytes, test_path, 'image/png')
        
        if url:
            print(f"✅ Image uploaded successfully!")
            print(f"   URL: {url}")
            
            # Clean up - delete test image
            print("Cleaning up test image...")
            supabase_service.delete_image(test_path)
            print("✅ Test image deleted")
            return True
        else:
            print("❌ Image upload failed")
            return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False


def test_database_tables():
    """Test if required database tables exist"""
    print("\n=== Testing Database Tables ===")
    try:
        # Try to query presentations table
        response = supabase_service.client.table('presentations').select('count', count='exact').limit(0).execute()
        print("✅ 'presentations' table exists")
        
        # Try to query slides table
        response = supabase_service.client.table('slides').select('count', count='exact').limit(0).execute()
        print("✅ 'slides' table exists")
        
        # Try to query users table (auth.users)
        # Note: We can't directly query auth.users, but we can check if our users table exists
        try:
            response = supabase_service.client.table('users').select('count', count='exact').limit(0).execute()
            print("✅ 'users' table exists")
        except:
            print("⚠️  'users' table might not exist (optional)")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("\nMake sure you've run the database migration SQL:")
        print("See SUPABASE_SETUP_GUIDE.md for SQL schema")
        return False


def main():
    print("=" * 50)
    print("SUPABASE INTEGRATION TEST")
    print("=" * 50)
    
    # Check environment variables
    print("\n=== Checking Environment Variables ===")
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is NOT set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    # Run tests
    tests = [
        test_supabase_connection,
        test_storage_bucket,
        test_image_upload,
        test_database_tables
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🎉 Supabase is fully configured and ready to use!")
        return True
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nPlease fix the failing tests before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
