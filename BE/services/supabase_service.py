"""
Supabase Service
Handles Supabase initialization, PostgreSQL database, and object storage
Images stored as files in storage bucket (not base64)
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client
import requests

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
STORAGE_BUCKET = 'fyp'


class SupabaseService:
    """Supabase service for database operations and image storage"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SupabaseService._initialized:
            self._initialize_supabase()
            SupabaseService._initialized = True
    
    def _initialize_supabase(self):
        """
        Initialize Supabase client using service role key for backend operations
        
        Environment variables required:
        - SUPABASE_URL: Project URL
        - SUPABASE_SERVICE_ROLE_KEY: Service role key (for backend)
        """
        try:
            if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError(
                    "Missing Supabase credentials. Ensure .env file has:\n"
                    "- SUPABASE_URL\n"
                    "- SUPABASE_SERVICE_ROLE_KEY"
                )
            
            # Initialize with service role key (for backend operations)
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            
            logger.info("Supabase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Try a simple query
            response = self.client.table('presentations').select('count', count='exact').execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    # ==================== Authentication ====================
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user from users table
        
        Args:
            user_id: User's UUID
            
        Returns:
            User information dictionary or None if not found
        """
        try:
            # Use eq() instead of single() to handle cases where user doesn't exist
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            if response.data and len(response.data) > 0:
                logger.info(f"Retrieved user {user_id}")
                return response.data[0]
            logger.warning(f"User {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def create_user(self, user_id: str, email: str, display_name: str = None) -> bool:
        """
        Create user profile in users table
        Note: This should only be called AFTER the user exists in Supabase Auth
        
        Args:
            user_id: User's UUID from auth
            email: User's email
            display_name: User's display name (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if user already exists
            existing = self.get_user(user_id)
            if existing:
                logger.info(f"User {user_id} already exists")
                return True
            
            user_data = {
                'id': user_id,
                'email': email,
                'display_name': display_name or email.split('@')[0]
            }
            self.client.table('users').insert(user_data).execute()
            logger.info(f"Created user profile for {user_id}")
            return True
        except Exception as e:
            # If it's a foreign key error, user doesn't exist in auth yet
            if '23503' in str(e) or 'foreign key' in str(e).lower():
                logger.warning(f"User {user_id} does not exist in Supabase Auth yet. Create auth user first.")
            else:
                logger.error(f"Failed to create user profile: {e}")
            return False
    
    # ==================== Image Storage ====================
    
    def upload_image(self, image_bytes: bytes, destination_path: str, content_type: str = 'image/jpeg') -> Optional[str]:
        """
        Upload image to Supabase storage bucket
        
        Args:
            image_bytes: Image data as bytes
            destination_path: Path in bucket (e.g., 'user_id/presentation_id/slide_1.jpg')
            content_type: MIME type of image
            
        Returns:
            Public URL of uploaded image or None if failed
        """
        try:
            # Upload to storage
            response = self.client.storage.from_(STORAGE_BUCKET).upload(
                path=destination_path,
                file=image_bytes,
                file_options={"content-type": content_type}
            )
            
            # Generate public URL
            public_url = self.client.storage.from_(STORAGE_BUCKET).get_public_url(destination_path)
            
            logger.info(f"Uploaded image to {destination_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None
    
    def upload_image_from_path(self, image_path: str, destination_path: str) -> Optional[str]:
        """
        Upload image from file path to storage bucket
        
        Args:
            image_path: Local path to image file
            destination_path: Path in bucket (e.g., 'user_id/presentation_id/slide_1.jpg')
            
        Returns:
            Public URL of uploaded image or None if failed
        """
        try:
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
            
            # Determine content type based on file extension
            ext = image_path.lower().split('.')[-1]
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            content_type = content_type_map.get(ext, 'image/jpeg')
            
            return self.upload_image(image_bytes, destination_path, content_type)
            
        except Exception as e:
            logger.error(f"Failed to upload image from {image_path}: {e}")
            return None
    
    def download_image(self, storage_path: str) -> Optional[bytes]:
        """
        Download image from storage bucket
        
        Args:
            storage_path: Path to image in bucket
            
        Returns:
            Image bytes or None if failed
        """
        try:
            response = self.client.storage.from_(STORAGE_BUCKET).download(storage_path)
            logger.info(f"Downloaded image from {storage_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to download image from {storage_path}: {e}")
            return None
    
    def delete_image(self, storage_path: str) -> bool:
        """
        Delete image from storage bucket
        
        Args:
            storage_path: Path to image in bucket
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.storage.from_(STORAGE_BUCKET).remove([storage_path])
            logger.info(f"Deleted image at {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return False
    
    def get_public_url(self, storage_path: str) -> Optional[str]:
        """
        Get public URL for image in storage bucket
        
        Args:
            storage_path: Path to image in bucket
            
        Returns:
            Public URL or None if failed
        """
        try:
            url = self.client.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
            return url
        except Exception as e:
            logger.error(f"Failed to get public URL: {e}")
            return None
    
    # ==================== Database - Presentations ====================
    
    def create_presentation(self, user_id: str, presentation_data: Dict) -> Optional[str]:
        """
        Create a new presentation in database
        Note: User must exist in users table first
        
        Args:
            user_id: User's UUID
            presentation_data: Presentation metadata
                - topic (str): Presentation topic
                - theme (str): Theme name
                - content_sources (list, optional): Content sources
                - brand_colors (dict, optional): Brand colors
            
        Returns:
            Presentation ID or None if failed
        """
        try:
            # Verify user exists
            user = self.get_user(user_id)
            if not user:
                logger.warning(f"Cannot create presentation: User {user_id} does not exist")
                return None
            
            ppt_id = str(uuid.uuid4())
            
            doc_data = {
                'ppt_id': ppt_id,
                'user_id': user_id,
                'topic': presentation_data.get('topic', ''),
                'theme': presentation_data.get('theme', 'modern'),
                'slide_count': 0,
                'content_sources': presentation_data.get('content_sources', []),
                'brand_colors': presentation_data.get('brand_colors')
            }
            
            self.client.table('presentations').insert(doc_data).execute()
            
            logger.info(f"Created presentation {ppt_id} for user {user_id}")
            return ppt_id
            
        except Exception as e:
            if '23503' in str(e) or 'foreign key' in str(e).lower():
                logger.warning(f"User {user_id} does not exist in users table. Create user first.")
            else:
                logger.error(f"Failed to create presentation: {e}")
            return None
    
    def get_presentation(self, ppt_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get presentation by ID
        
        Args:
            ppt_id: Presentation ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Presentation data or None if not found/unauthorized
        """
        try:
            response = self.client.table('presentations').select('*').eq('ppt_id', ppt_id).execute()
            
            if not response.data or len(response.data) == 0:
                logger.warning(f"Presentation {ppt_id} not found")
                return None
            
            data = response.data[0]
            
            # Check authorization if user_id provided
            if user_id and data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to access presentation {ppt_id}")
                return None
            
            # Fetch slides for this presentation
            slides_response = self.client.table('slides').select('*').eq('presentation_id', data['id']).order('slide_index').execute()
            data['slides'] = slides_response.data if slides_response.data else []
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get presentation {ppt_id}: {e}")
            return None
    
    def update_presentation(self, ppt_id: str, user_id: str, updates: Dict) -> bool:
        """
        Update presentation
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get presentation first
            response = self.client.table('presentations').select('*').eq('ppt_id', ppt_id).single().execute()
            
            if not response.data:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            data = response.data
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to update presentation {ppt_id}")
                return False
            
            # Update
            updates['updated_at'] = datetime.now().isoformat()
            self.client.table('presentations').update(updates).eq('id', data['id']).execute()
            
            logger.info(f"Updated presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update presentation: {e}")
            return False
    
    def delete_presentation(self, ppt_id: str, user_id: str) -> bool:
        """
        Delete presentation and associated slides/images
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.table('presentations').select('*').eq('ppt_id', ppt_id).single().execute()
            
            if not response.data:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            data = response.data
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to delete presentation {ppt_id}")
                return False
            
            # Delete images from storage
            slides_response = self.client.table('slides').select('*').eq('presentation_id', data['id']).execute()
            deleted_count = 0
            for slide in slides_response.data or []:
                if slide.get('image_url'):
                    # Extract storage path from URL
                    storage_path = self._extract_storage_path(slide['image_url'])
                    if storage_path and self.delete_image(storage_path):
                        deleted_count += 1
            
            # Delete slides (cascade will handle this, but explicit for clarity)
            self.client.table('slides').delete().eq('presentation_id', data['id']).execute()
            
            # Delete presentation
            self.client.table('presentations').delete().eq('id', data['id']).execute()
            
            logger.info(f"Deleted presentation {ppt_id} ({deleted_count} images from storage)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete presentation: {e}")
            return False
    
    def get_user_presentations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get all presentations for a user, ordered by creation date
        
        Args:
            user_id: User's UUID
            limit: Maximum number of presentations to return
            
        Returns:
            List of presentation metadata
        """
        try:
            response = self.client.table('presentations').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            
            presentations = response.data if response.data else []
            logger.info(f"Retrieved {len(presentations)} presentations for user {user_id}")
            return presentations
            
        except Exception as e:
            logger.error(f"Failed to get user presentations: {e}")
            return []
    
    # ==================== Database - Slides ====================
    
    def add_slide_to_presentation(self, ppt_id: str, user_id: str, slide_data: Dict) -> bool:
        """
        Add a new slide to presentation
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            slide_data: Slide data
                - title (str): Slide title
                - content (str): Slide content
                - image_url (str): URL of uploaded image
                - slide_index (int): Position in presentation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get presentation
            pres_response = self.client.table('presentations').select('*').eq('ppt_id', ppt_id).single().execute()
            
            if not pres_response.data:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            pres_data = pres_response.data
            
            # Check authorization
            if pres_data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to modify presentation {ppt_id}")
                return False
            
            # Create slide
            slide_insert = {
                'presentation_id': pres_data['id'],
                'title': slide_data.get('title', ''),
                'content': slide_data.get('content', ''),
                'image_url': slide_data.get('image_url'),
                'slide_index': slide_data.get('slide_index', 0)
            }
            
            self.client.table('slides').insert(slide_insert).execute()
            
            # Update slide count
            new_count = pres_data.get('slide_count', 0) + 1
            self.client.table('presentations').update({'slide_count': new_count}).eq('id', pres_data['id']).execute()
            
            logger.info(f"Added slide to presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add slide: {e}")
            return False
    
    def delete_slide_from_presentation(self, ppt_id: str, user_id: str, slide_index: int) -> bool:
        """
        Delete a slide from presentation
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            slide_index: Index of slide to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get presentation
            pres_response = self.client.table('presentations').select('*').eq('ppt_id', ppt_id).single().execute()
            
            if not pres_response.data:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            pres_data = pres_response.data
            
            # Check authorization
            if pres_data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to modify presentation {ppt_id}")
                return False
            
            # Get slide
            slides_response = self.client.table('slides').select('*').eq('presentation_id', pres_data['id']).eq('slide_index', slide_index).single().execute()
            
            if not slides_response.data:
                logger.warning(f"Slide at index {slide_index} not found")
                return False
            
            slide = slides_response.data
            
            # Delete image if exists
            if slide.get('image_url'):
                storage_path = self._extract_storage_path(slide['image_url'])
                if storage_path:
                    self.delete_image(storage_path)
            
            # Delete slide
            self.client.table('slides').delete().eq('id', slide['id']).execute()
            
            # Update slide count
            new_count = max(0, pres_data.get('slide_count', 1) - 1)
            self.client.table('presentations').update({'slide_count': new_count}).eq('id', pres_data['id']).execute()
            
            logger.info(f"Deleted slide from presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete slide: {e}")
            return False
    
    def get_slides(self, ppt_id: str, user_id: str) -> Optional[List[Dict]]:
        """
        Get all slides for a presentation
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            
        Returns:
            List of slides or None if unauthorized
        """
        try:
            # Get presentation
            pres_response = self.client.table('presentations').select('*').eq('ppt_id', ppt_id).single().execute()
            
            if not pres_response.data:
                return None
            
            pres_data = pres_response.data
            
            # Check authorization
            if pres_data.get('user_id') != user_id:
                return None
            
            # Get slides
            slides_response = self.client.table('slides').select('*').eq('presentation_id', pres_data['id']).order('slide_index').execute()
            
            return slides_response.data if slides_response.data else []
            
        except Exception as e:
            logger.error(f"Failed to get slides: {e}")
            return None
    
    # ==================== Helper Methods ====================
    
    def _extract_storage_path(self, public_url: str) -> Optional[str]:
        """
        Extract storage path from public URL
        
        Args:
            public_url: Public URL from storage
            
        Returns:
            Storage path or None if unable to extract
        """
        try:
            # URL format: https://xxxx.supabase.co/storage/v1/object/public/bucket/path
            if '/object/public/' in public_url:
                parts = public_url.split('/object/public/')
                if len(parts) > 1:
                    full_path = parts[1]
                    # Remove bucket name from path
                    if f'{STORAGE_BUCKET}/' in full_path:
                        return full_path.split(f'{STORAGE_BUCKET}/', 1)[1]
            return None
        except Exception as e:
            logger.error(f"Failed to extract storage path: {e}")
            return None


# Singleton instance
supabase_service = SupabaseService()
