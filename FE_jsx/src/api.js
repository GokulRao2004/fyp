import axios from 'axios';

const API_BASE = '/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
});

// Add auth token to requests if available
export function setAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
}

// Generate a new presentation
export async function generatePPT(data) {
  const response = await apiClient.post('/generate', data);
  return response.data;
}

// Get presentation metadata
export async function getPPTMetadata(pptId) {
  const response = await apiClient.get(`/ppt/${pptId}`);
  return response.data;
}

// Download presentation file
export async function downloadPPT(pptId) {
  const response = await apiClient.get(`/download/${pptId}`, {
    responseType: 'blob'
  });
  return response.data;
}

// Delete presentation
export async function deletePPT(pptId) {
  const response = await apiClient.delete(`/ppt/${pptId}`);
  return response.data;
}

// Update a specific slide
export async function updateSlide(pptId, slideIndex, slideData) {
  const response = await apiClient.patch(
    `/ppt/${pptId}/slide/${slideIndex}`,
    slideData
  );
  return response.data;
}

// Replace image in a slide
export async function replaceImage(data) {
  const response = await apiClient.post('/replace-image', data);
  return response.data;
}

// Search for images on Pixabay
export async function searchPixabayImages(query, page = 1, perPage = 20) {
  const response = await apiClient.get('/pixabay/search', {
    params: { q: query, page, per_page: perPage }
  });
  return response.data;
}

// Upload source document
export async function uploadSource(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/upload-source', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
}

// Check robots.txt for a URL
export async function checkRobots(url) {
  const response = await apiClient.get('/robots-check', {
    params: { url }
  });
  return response.data;
}

// Check multiple URLs for robots.txt compliance
export async function checkMultipleUrls(urls) {
  const results = await Promise.all(
    urls.map(async (url) => {
      try {
        const result = await checkRobots(url);
        return { url, ...result };
      } catch (error) {
        return { 
          url, 
          allowed: false, 
          message: error.response?.data?.error || 'Failed to check URL' 
        };
      }
    })
  );
  return results;
}
