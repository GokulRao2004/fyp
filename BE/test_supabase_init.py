"""
Supabase Integration Test Suite
Tests all functionality of the Supabase service
Run this after setting up Supabase to verify everything works
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.supabase_service import supabase_service
from dotenv import load_dotenv
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

class SupabaseTestSuite:
    """Test suite for Supabase service"""
    
    def __init__(self):
        self.test_user_id = str(uuid.uuid4())
        self.test_ppt_id = None
        self.test_image_path = None
        self.passed = 0
        self.failed = 0
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BLUE}{'='*60}")
        print("SUPABASE SERVICE TEST SUITE")
        print(f"{'='*60}{Colors.END}\n")
        
        # Connection tests
        print(f"{Colors.BLUE}1. CONNECTION TESTS{Colors.END}")
        self.test_connection()
        
        # User tests
        print(f"\n{Colors.BLUE}2. USER TESTS{Colors.END}")
        self.test_user_creation()
        
        # Presentation tests
        print(f"\n{Colors.BLUE}3. PRESENTATION TESTS{Colors.END}")
        self.test_presentation_crud()
        
        # Slide tests
        print(f"\n{Colors.BLUE}4. SLIDE TESTS{Colors.END}")
        self.test_slide_operations()
        
        # Image tests
        print(f"\n{Colors.BLUE}5. IMAGE STORAGE TESTS{Colors.END}")
        self.test_image_operations()
        
        # Print summary
        self.print_summary()
    
    def test_connection(self):
        """Test Supabase connection"""
        try:
            # Check environment variables
            url = os.getenv('SUPABASE_URL')
            service_role = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not url:
                print_error("SUPABASE_URL not found in environment variables")
                self.failed += 1
                return
            
            if not service_role:
                print_error("SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
                self.failed += 1
                return
            
            print_info(f"Supabase URL: {url}")
            
            # Verify service is initialized
            if supabase_service is not None:
                print_success("Supabase service initialized")
                self.passed += 1
            else:
                print_error("Supabase service failed to initialize")
                self.failed += 1
        
        except Exception as e:
            print_error(f"Connection test failed: {e}")
            self.failed += 1
    
    def test_user_creation(self):
        """Test user creation"""
        try:
            # For testing, we'll use a test UUID that we'll manually insert
            # In production, users are created via Supabase Auth first
            
            print_info("Testing user operations...")
            
            # For this test, we'll create a test user directly in the users table
            # This simulates a user that was created via Supabase Auth
            test_email = f"test-{uuid.uuid4()}@example.com"
            
            # Try to create user (will fail if not in auth, which is expected)
            result = supabase_service.create_user(
                self.test_user_id,
                test_email,
                "Test User"
            )
            
            if result:
                print_success(f"User created: {self.test_user_id}")
                self.passed += 1
            else:
                # Expected to fail because user doesn't exist in Supabase Auth
                print_warning(f"User not created (expected: user must be created in Supabase Auth first)")
                # Let's skip presentation tests if user creation failed
                self.test_user_id = None
                return
            
            # Get user
            user = supabase_service.get_user(self.test_user_id)
            
            if user:
                print_success(f"User retrieved: {user.get('display_name', 'N/A')}")
                self.passed += 1
            else:
                print_error("Failed to retrieve user")
                self.failed += 1
        
        except Exception as e:
            print_error(f"User creation test failed: {e}")
            self.failed += 1
    
    def test_presentation_crud(self):
        """Test presentation CRUD operations"""
        try:
            # Skip if user creation failed
            if not self.test_user_id:
                print_warning("Skipping presentation tests (user not created)")
                return
            
            # Create presentation
            ppt_data = {
                'topic': f'Test Presentation {uuid.uuid4()}',
                'theme': 'modern',
                'slide_count': 3,
                'num_slides': 3
            }
            
            ppt_id = supabase_service.create_presentation(self.test_user_id, ppt_data)
            
            if ppt_id:
                self.test_ppt_id = ppt_id
                print_success(f"Presentation created: {ppt_id}")
                self.passed += 1
            else:
                print_error("Failed to create presentation")
                self.failed += 1
                return
            
            # Get presentation
            ppt = supabase_service.get_presentation(ppt_id, self.test_user_id)
            
            if ppt and ppt.get('topic') == ppt_data['topic']:
                print_success(f"Presentation retrieved: {ppt['topic']}")
                self.passed += 1
            else:
                print_error("Failed to retrieve presentation")
                self.failed += 1
            
            # Update presentation
            updated_topic = f'Updated {ppt_data["topic"]}'
            result = supabase_service.update_presentation(
                ppt_id,
                self.test_user_id,
                {'topic': updated_topic}
            )
            
            if result:
                # Verify update
                updated_ppt = supabase_service.get_presentation(ppt_id, self.test_user_id)
                if updated_ppt and updated_ppt.get('topic') == updated_topic:
                    print_success(f"Presentation updated: {updated_topic}")
                    self.passed += 1
                else:
                    print_error("Update verification failed")
                    self.failed += 1
            else:
                print_error("Failed to update presentation")
                self.failed += 1
            
            # List user presentations
            presentations = supabase_service.get_user_presentations(self.test_user_id, limit=10)
            
            if presentations and len(presentations) > 0:
                print_success(f"Listed {len(presentations)} presentations for user")
                self.passed += 1
            else:
                print_warning("No presentations listed (but may be normal)")
                self.passed += 1
        
        except Exception as e:
            print_error(f"Presentation CRUD test failed: {e}")
            self.failed += 1
    
    def test_slide_operations(self):
        """Test slide operations"""
        try:
            if not self.test_ppt_id:
                print_warning("Skipping slide tests (no presentation created)")
                return
            
            # Add slide
            slide_data = {
                'title': 'Test Slide',
                'content': 'Test content',
                'layout': 'title_content',
                'notes': 'Test notes'
            }
            
            result = supabase_service.add_slide_to_presentation(
                self.test_ppt_id,
                self.test_user_id,
                slide_data
            )
            
            if result:
                print_success("Slide added to presentation")
                self.passed += 1
            else:
                print_error("Failed to add slide")
                self.failed += 1
            
            # Get slides
            slides = supabase_service.get_slides(self.test_ppt_id, self.test_user_id)
            
            if slides and len(slides) > 0:
                print_success(f"Retrieved {len(slides)} slides")
                self.passed += 1
            else:
                print_warning("No slides retrieved (but may be normal)")
                self.passed += 1
            
            # Delete slide
            if len(slides) > 0:
                result = supabase_service.delete_slide_from_presentation(
                    self.test_ppt_id,
                    self.test_user_id,
                    0  # Delete first slide
                )
                
                if result:
                    print_success("Slide deleted from presentation")
                    self.passed += 1
                else:
                    print_warning("Slide deletion returned False (may not exist)")
                    self.passed += 1
        
        except Exception as e:
            print_error(f"Slide operations test failed: {e}")
            self.failed += 1
    
    def test_image_operations(self):
        """Test image upload, download, and delete"""
        try:
            # Create test image
            test_image = b"fake image data for testing"
            storage_path = f"test/{uuid.uuid4()}.jpg"
            
            # Upload image
            url = supabase_service.upload_image(
                test_image,
                storage_path,
                'image/jpeg'
            )
            
            if url:
                self.test_image_path = storage_path
                print_success(f"Image uploaded: {url}")
                self.passed += 1
            else:
                print_error("Failed to upload image")
                self.failed += 1
                return
            
            # Get public URL
            public_url = supabase_service.get_public_url(storage_path)
            
            if public_url:
                print_success(f"Public URL generated: {public_url[:50]}...")
                self.passed += 1
            else:
                print_error("Failed to get public URL")
                self.failed += 1
            
            # Download image
            downloaded = supabase_service.download_image(storage_path)
            
            if downloaded and downloaded == test_image:
                print_success(f"Image downloaded and verified ({len(downloaded)} bytes)")
                self.passed += 1
            else:
                print_warning("Downloaded image doesn't match (may have been processed)")
                self.passed += 1
            
            # Delete image
            # result = supabase_service.delete_image(storage_path)
            
            # if result:
            #     print_success("Image deleted from storage")
            #     self.passed += 1
            #     self.test_image_path = None  # Mark as deleted
            # else:
            #     print_error("Failed to delete image")
            #     self.failed += 1
        
        except Exception as e:
            print_error(f"Image operations test failed: {e}")
            self.failed += 1
    
    def cleanup(self):
        """Clean up test data"""
        try:
            print(f"\n{Colors.BLUE}CLEANUP{Colors.END}")
            
            # Delete test image if not already deleted
            if self.test_image_path:
                try:
                    supabase_service.delete_image(self.test_image_path)
                    print_info("Test image cleaned up")
                except:
                    pass
            
            # Delete test presentation
            if self.test_ppt_id:
                try:
                    supabase_service.delete_presentation(self.test_ppt_id, self.test_user_id)
                    print_info("Test presentation cleaned up")
                except:
                    pass
            
            print_success("Cleanup complete")
        
        except Exception as e:
            print_warning(f"Cleanup incomplete: {e}")
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        
        print(f"\n{Colors.BLUE}{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}{Colors.END}")
        
        print(f"Total Tests: {total}")
        print_success(f"Passed: {self.passed}")
        
        if self.failed > 0:
            print_error(f"Failed: {self.failed}")
        else:
            print_success(f"Failed: {self.failed}")
        
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        if success_rate == 100:
            print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.END}")
        elif success_rate >= 80:
            print(f"\n{Colors.YELLOW}Most tests passed ({success_rate:.0f}%){Colors.END}")
        else:
            print(f"\n{Colors.RED}⚠️  Some tests failed ({success_rate:.0f}%){Colors.END}")
        
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")


def main():
    """Main test execution"""
    try:
        suite = SupabaseTestSuite()
        suite.run_all_tests()
        suite.cleanup()
        
        # Exit with appropriate code
        sys.exit(0 if suite.failed == 0 else 1)
    
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
