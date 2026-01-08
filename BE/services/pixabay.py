"""
Pixabay Image Scraper Module
Adapted from final_year_project-main/pixabay_scraper.py
Fetches relevant royalty-free images from Pixabay API
"""
import os
import requests
from typing import List, Optional, Dict
from urllib.parse import urlencode
import time
import logging

logger = logging.getLogger(__name__)


class PixabayClient:
    """Client for Pixabay API interactions"""
    
    BASE_URL = "https://pixabay.com/api/"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Pixabay API client
        
        Args:
            api_key: Pixabay API key (defaults to PIXABAY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('PIXABAY_API_KEY')
        
        if not self.api_key:
            raise ValueError("PIXABAY_API_KEY is required. Set it in environment or pass as parameter.")
    
    def search_images(
        self, 
        query: str, 
        per_page: int = 5,
        page: int = 1,
        image_type: str = "photo",
        orientation: str = "horizontal",
        safesearch: bool = True
    ) -> List[Dict]:
        """
        Search for images on Pixabay
        
        Args:
            query: Search keywords
            per_page: Number of results to return (default: 5, max: 200)
            page: Page number for pagination
            image_type: Type of image (photo, illustration, vector)
            orientation: Image orientation (horizontal, vertical, all)
            safesearch: Enable safe search
        
        Returns:
            List of image data dictionaries
        """
        params = {
            'key': self.api_key,
            'q': query,
            'per_page': min(per_page, 200),  # Pixabay max is 200
            'page': page,
            'image_type': image_type,
            'orientation': orientation,
            'safesearch': str(safesearch).lower()
        }
        
        try:
            logger.info(f"Searching Pixabay for: {query}")
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('hits'):
                logger.info(f"Found {len(data['hits'])} images for query: {query}")
                return data['hits']
            else:
                logger.warning(f"No images found for query: {query}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching images from Pixabay: {e}")
            return []
    
    def download_and_upload_image(
        self, 
        image_url: str, 
        storage_destination_path: str,
        storage_service
    ) -> Optional[str]:
        """
        Download an image from URL and upload to Supabase Storage
        
        Args:
            image_url: URL of the image to download
            storage_destination_path: Path in Supabase Storage (e.g., 'users/uid/images/slide_1.jpg')
            storage_service: Supabase service instance
        
        Returns:
            Supabase public URL if successful, None otherwise
        """
        try:
            response = requests.get(image_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Read image bytes
            image_bytes = b''
            for chunk in response.iter_content(chunk_size=8192):
                image_bytes += chunk
            
            # Upload to Supabase Storage
            supabase_url = storage_service.upload_image_from_bytes(
                image_bytes, 
                storage_destination_path, 
                content_type='image/jpeg'
            )
            
            if supabase_url:
                logger.info(f"Uploaded image to Supabase: {storage_destination_path}")
                return supabase_url
            else:
                logger.error(f"Failed to upload image to Supabase")
                return None
            
        except Exception as e:
            logger.error(f"Error downloading/uploading image: {e}")
            return None
    
    def get_best_image(self, query: str, orientation: str = "horizontal") -> Optional[Dict]:
        """
        Get the best (highest quality) image for a query
        
        Args:
            query: Search keywords
            orientation: Image orientation preference
        
        Returns:
            Image data dictionary or None
        """
        images = self.search_images(query, per_page=3, orientation=orientation)
        
        if not images:
            return None
        
        # Sort by quality metrics (likes, views, etc.)
        best_image = max(images, key=lambda x: x.get('likes', 0) + x.get('views', 0) / 1000)
        
        logger.info(f"Selected best image for '{query}': ID {best_image.get('id')}")
        return best_image
    
    def download_slide_image_to_storage(
        self, 
        keywords: str, 
        slide_number: int,
        storage_destination_path: str,
        storage_service
    ) -> Optional[str]:
        """
        Download an image for a specific slide and upload to Supabase
        
        Args:
            keywords: Search keywords
            slide_number: Slide number for reference
            storage_destination_path: Path in Supabase Storage
            storage_service: Supabase service instance
        
        Returns:
            Supabase public URL or None
        """
        image_data = self.get_best_image(keywords)
        
        if not image_data:
            logger.warning(f"No image found for slide {slide_number} with keywords: {keywords}")
            return None
        
        # Use webformatURL for good quality
        image_url = image_data.get('webformatURL') or image_data.get('largeImageURL')
        
        if not image_url:
            return None
        
        # Upload to Supabase
        supabase_url = self.download_and_upload_image(image_url, storage_destination_path, storage_service)
        
        if supabase_url:
            logger.info(f"Uploaded image for slide {slide_number}: {keywords}")
            return supabase_url
        else:
            return None
    
    def download_all_slide_images_to_storage(
        self, 
        slides_data: List[Dict],
        user_id: str,
        presentation_topic: str,
        storage_service
    ) -> Dict[int, str]:
        """
        Download images for all slides and upload to Supabase
        
        Args:
            slides_data: List of slide dictionaries with image_keywords
            user_id: User ID for storage path
            presentation_topic: Presentation topic for path
            storage_service: Supabase service instance
        
        Returns:
            Dictionary mapping slide numbers to Supabase URLs
        """
        image_urls = {}
        
        for slide in slides_data:
            slide_num = slide.get('slide_number')
            keywords = slide.get('image_keywords', '')
            
            if not keywords:
                continue
            
            # Create storage path
            storage_path = f"users/{user_id}/presentations/{presentation_topic.replace(' ', '_')}/slide_{slide_num}.jpg"
            
            url = self.download_slide_image_to_storage(keywords, slide_num, storage_path, storage_service)
            
            if url:
                image_urls[slide_num] = url
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        logger.info(f"Uploaded {len(image_urls)} images to Supabase")
        return image_urls
    
    def get_image_suggestions(self, query: str, count: int = 5) -> List[Dict]:
        """
        Get image suggestions with metadata for frontend display
        
        Args:
            query: Search query
            count: Number of suggestions to return
            
        Returns:
            List of image metadata dictionaries
        """
        images = self.search_images(query, per_page=count)
        
        suggestions = []
        for img in images:
            suggestions.append({
                'id': str(img.get('id')),
                'preview_url': img.get('previewURL'),
                'webformat_url': img.get('webformatURL'),
                'large_url': img.get('largeImageURL'),
                'keywords': img.get('tags', query),
                'user': img.get('user', 'Unknown'),
                'page_url': img.get('pageURL')
            })
        
        return suggestions
