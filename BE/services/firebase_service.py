"""
Firebase Service
Handles Firebase Admin SDK initialization, authentication, and Firestore
All images are stored as base64 strings in Firestore
"""
import os
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth, firestore
from typing import Optional, Dict, List, Any
import uuid
import base64


logger = logging.getLogger(__name__)

# Firebase configuration
# All images stored as base64 in Firestore - no Cloud Storage bucket needed


class FirebaseService:
    """Firebase service for authentication, storage, and database operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FirebaseService._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """
        Initialize Firebase Admin SDK using service-key.json in the BE/ directory
        
        Credential lookup order:
        1. service-key.json in parent directory (BE/)
        2. GOOGLE_APPLICATION_CREDENTIALS environment variable
        3. Application Default Credentials (gcloud auth, Cloud Run, etc.)
        """
        try:
            # Check if Firebase is already initialized
            try:
                # If already initialized, just get Firestore client
                if firebase_admin._apps:
                    logger.info("Firebase already initialized")
                    self.db = firestore.client()
                    return
            except AttributeError:
                # _apps might not exist in some versions, proceed with initialization
                pass
            
            cred = None
            service_key_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'service-key.json'
            )
            
            # Option 2: Primary - Use service-key.json from BE/ directory
            if os.path.exists(service_key_path):
                logger.info(f"Using service account key from {service_key_path}")
                cred = credentials.Certificate(service_key_path)
            # Option 1: Secondary - Check GOOGLE_APPLICATION_CREDENTIALS environment variable
            elif os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                logger.info("Using GOOGLE_APPLICATION_CREDENTIALS environment variable")
                cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
            # Option 3: Tertiary - Try Application Default Credentials
            else:
                logger.info("Attempting to use Application Default Credentials")
                try:
                    cred = credentials.ApplicationDefault()
                except Exception as e:
                    logger.warning(f"ApplicationDefault failed: {e}")
                    raise FileNotFoundError(
                        f"Service account key not found at {service_key_path} and "
                        f"GOOGLE_APPLICATION_CREDENTIALS not set. "
                        f"Please place service-key.json in the BE/ directory."
                    )
            
            # Initialize Firebase Admin SDK with the credential (Firestore only)
            firebase_admin.initialize_app(cred)
            
            # Initialize Firestore client
            self.db = firestore.client()
            
            logger.info("Firebase initialized successfully (Firestore only - images stored as base64)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    # ==================== Authentication ====================
    
    def verify_token(self, id_token: str) -> Optional[Dict]:
        """
        Verify Firebase ID token
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Decoded token with user info or None if invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def get_user(self, uid: str) -> Optional[Dict]:
        """
        Get user by UID from Firebase Authentication
        
        Args:
            uid: User's Firebase UID
            
        Returns:
            User information dictionary or None if not found
        """
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified
            }
        except Exception as e:
            logger.error(f"Failed to get user {uid}: {e}")
            return None
    
    # ==================== Image Processing (Base64 Only) ====================
    
    def convert_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Convert image file to base64 string
        
        Args:
            image_path: Local path to image file
            
        Returns:
            Base64-encoded image string, or None if failed
        """
        try:
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            logger.info(f"Converted image from {image_path} to base64")
            return image_base64
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {e}")
            return None
    
    def convert_bytes_to_base64(self, image_bytes: bytes) -> Optional[str]:
        """
        Convert image bytes to base64 string
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Base64-encoded image string, or None if failed
        """
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            logger.info(f"Converted image bytes to base64")
            return image_base64
        except Exception as e:
            logger.error(f"Failed to convert bytes to base64: {e}")
            return None
    
    def convert_base64_to_bytes(self, image_base64: str) -> Optional[bytes]:
        """
        Convert base64 string to image bytes
        
        Args:
            image_base64: Base64-encoded image string (with or without data URI prefix)
            
        Returns:
            Image data as bytes, or None if failed
        """
        try:
            # Remove data URI prefix if present (e.g., 'data:image/jpeg;base64,')
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_bytes = base64.b64decode(image_base64)
            logger.info(f"Converted base64 to image bytes")
            return image_bytes
        except Exception as e:
            logger.error(f"Failed to convert base64 to bytes: {e}")
            return None
    
    # ==================== Firestore - Presentations ====================
    
    def create_presentation(self, user_id: str, presentation_data: Dict) -> str:
        """
        Create a new presentation document in Firestore
        
        Args:
            user_id: User's Firebase UID
            presentation_data: Dictionary with presentation metadata and slides
                - topic (str): Presentation topic
                - theme (str): Theme name
                - slides (list): List of slide objects (each with base64-encoded images)
                - content_sources (list, optional): Content sources used
                - brand_colors (dict, optional): Brand color configuration
            
        Returns:
            Presentation ID (UUID)
            
        Raises:
            Exception: If presentation creation fails
            
        Note:
            Images in slides should be base64-encoded strings stored in Firestore
        """
        try:
            ppt_id = str(uuid.uuid4())
            
            # Process slides to ensure images are properly formatted
            slides = presentation_data.get('slides', [])
            processed_slides = []
            
            for slide in slides:
                processed_slide = slide.copy()
                # Image is already expected to be base64 from upload methods
                processed_slides.append(processed_slide)
            
            doc_data = {
                'ppt_id': ppt_id,
                'user_id': user_id,
                'topic': presentation_data.get('topic', ''),
                'theme': presentation_data.get('theme', 'modern'),
                'slides': processed_slides,
                'slide_count': len(processed_slides),
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'content_sources': presentation_data.get('content_sources', []),
                'brand_colors': presentation_data.get('brand_colors')
            }
            
            # Create document in Firestore
            self.db.collection('presentations').document(ppt_id).set(doc_data)
            
            logger.info(f"Created presentation {ppt_id} for user {user_id} with {len(processed_slides)} slides")
            return ppt_id
            
        except Exception as e:
            logger.error(f"Failed to create presentation: {e}")
            raise
    
    def get_presentation(self, ppt_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get presentation document from Firestore
        
        Args:
            ppt_id: Presentation ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Presentation data or None if not found/unauthorized
        """
        try:
            doc = self.db.collection('presentations').document(ppt_id).get()
            
            if not doc.exists:
                logger.warning(f"Presentation {ppt_id} not found")
                return None
            
            data = doc.to_dict()
            
            # Check authorization if user_id provided
            if user_id and data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to access presentation {ppt_id}")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get presentation {ppt_id}: {e}")
            return None
    
    def update_presentation(self, ppt_id: str, user_id: str, updates: Dict) -> bool:
        """
        Update presentation document in Firestore
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization check
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('presentations').document(ppt_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            data = doc.to_dict()
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to update presentation {ppt_id}")
                return False
            
            # Add updated timestamp
            updates['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.update(updates)
            
            logger.info(f"Updated presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update presentation: {e}")
            return False
    
    def delete_presentation(self, ppt_id: str, user_id: str) -> bool:
        """
        Delete presentation document from Firestore
        (Base64 images stored in Firestore are automatically deleted)
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization check
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('presentations').document(ppt_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            data = doc.to_dict()
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to delete presentation {ppt_id}")
                return False
            
            # Delete document from Firestore (all base64 images deleted with it)
            doc_ref.delete()
            
            logger.info(f"Deleted presentation {ppt_id} from Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete presentation: {e}")
            return False
    
    def get_user_presentations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get all presentations for a user from Firestore, ordered by creation date (newest first)
        
        Args:
            user_id: User's Firebase UID
            limit: Maximum number of presentations to return (default: 50)
            
        Returns:
            List of presentation metadata summaries with base64-encoded thumbnail images
        """
        try:
            query = (self.db.collection('presentations')
                    .where('user_id', '==', user_id)
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            docs = query.stream()
            
            presentations = []
            for doc in docs:
                data = doc.to_dict()
                # Extract thumbnail as base64 from first slide if available
                thumbnail_base64 = None
                if data.get('slides'):
                    first_slide = data['slides'][0]
                    # Image stored as base64 in slide
                    if first_slide.get('image_base64'):
                        thumbnail_base64 = first_slide['image_base64']
                
                presentations.append({
                    'ppt_id': data.get('ppt_id'),
                    'topic': data.get('topic'),
                    'theme': data.get('theme'),
                    'slide_count': data.get('slide_count', 0),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'thumbnail_base64': thumbnail_base64  # Base64-encoded thumbnail
                })
            
            logger.info(f"Retrieved {len(presentations)} presentations for user {user_id}")
            return presentations
            
        except Exception as e:
            logger.error(f"Failed to get user presentations: {e}")
            return []
    
    def add_slide_to_presentation(self, ppt_id: str, user_id: str, slide_data: Dict) -> bool:
        """
        Add a new slide to an existing presentation in Firestore
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            slide_data: Slide data with base64-encoded image
                - title (str): Slide title
                - content (str): Slide content
                - image_base64 (str): Base64-encoded image string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('presentations').document(ppt_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            data = doc.to_dict()
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to modify presentation {ppt_id}")
                return False
            
            # Add slide to array (base64 image stored as-is in Firestore)
            slides = data.get('slides', [])
            slides.append(slide_data)
            
            # Update presentation with new slides
            doc_ref.update({
                'slides': slides,
                'slide_count': len(slides),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Added slide to presentation {ppt_id} (total: {len(slides)})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add slide: {e}")
            return False
    
    def delete_slide_from_presentation(self, ppt_id: str, user_id: str, slide_index: int) -> bool:
        """
        Delete a slide from a presentation in Firestore
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            slide_index: Index of slide to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('presentations').document(ppt_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Presentation {ppt_id} not found")
                return False
            
            data = doc.to_dict()
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to modify presentation {ppt_id}")
                return False
            
            slides = data.get('slides', [])
            
            if slide_index < 0 or slide_index >= len(slides):
                logger.warning(f"Invalid slide index {slide_index} for presentation {ppt_id}")
                return False
            
            # Remove slide from array (base64 image removed from Firestore)
            slides.pop(slide_index)
            
            # Update presentation
            doc_ref.update({
                'slides': slides,
                'slide_count': len(slides),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Deleted slide {slide_index} from presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete slide: {e}")
            return False


# Singleton instance
firebase_service = FirebaseService()
