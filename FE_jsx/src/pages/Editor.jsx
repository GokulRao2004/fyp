import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getPPTMetadata, updateSlide, replaceImage, downloadPPT, searchPixabayImages } from '../api'
import SlidePreview from '../components/SlidePreview'

export default function Editor() {
  const { pptId } = useParams()
  const navigate = useNavigate()
  
  const [presentation, setPresentation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloading, setDownloading] = useState(false)
  const [showImageSearch, setShowImageSearch] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [activeSlideForImage, setActiveSlideForImage] = useState(null)

  useEffect(() => {
    loadPresentation()
  }, [pptId])

  const loadPresentation = async () => {
    try {
      const data = await getPPTMetadata(pptId)
      setPresentation(data)
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load presentation')
      setLoading(false)
    }
  }

  const handleSlideUpdate = async (slideIndex, updatedSlide) => {
    try {
      const result = await updateSlide(pptId, slideIndex, updatedSlide)
      setPresentation(result)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update slide')
    }
  }

  const handleImageChange = async (slideIndex, imageUrl) => {
    try {
      const result = await replaceImage({
        ppt_id: pptId,
        slide_index: slideIndex,
        new_image_url: imageUrl
      })
      setPresentation(result)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to replace image')
    }
  }

  const handleOpenImageSearch = (slideIndex) => {
    setActiveSlideForImage(slideIndex)
    const slide = presentation.slides[slideIndex]
    setSearchQuery(slide.title || '')
    setShowImageSearch(true)
  }

  const handleImageSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      const results = await searchPixabayImages(searchQuery)
      setSearchResults(results.images || [])
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to search images')
    }
  }

  const handleSelectSearchedImage = async (imageUrl) => {
    await handleImageChange(activeSlideForImage, imageUrl)
    setShowImageSearch(false)
    setSearchResults([])
    setActiveSlideForImage(null)
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const blob = await downloadPPT(pptId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${presentation.topic.replace(/\s+/g, '_')}.pptx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to download presentation')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading presentation...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
          <h3 className="font-semibold mb-2">Error</h3>
          <p>{error}</p>
          <button
            onClick={() => navigate('/generate')}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Generate New Presentation
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{presentation.topic}</h1>
            <p className="text-gray-600">
              Theme: <span className="font-semibold">{presentation.theme}</span> • 
              {presentation.slides.length} slides
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/generate')}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              New Presentation
            </button>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {downloading ? 'Downloading...' : 'Download PPTX'}
            </button>
          </div>
        </div>

        {/* Slides */}
        <div className="space-y-6">
          {presentation.slides.map((slide, index) => (
            <SlidePreview
              key={index}
              slide={slide}
              slideIndex={index}
              onUpdate={handleSlideUpdate}
              onImageChange={handleImageChange}
            />
          ))}
        </div>

        {/* Image Search Modal */}
        {showImageSearch && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">Search Images</h2>
                  <button
                    onClick={() => {
                      setShowImageSearch(false)
                      setSearchResults([])
                    }}
                    className="text-gray-500 hover:text-gray-700 text-2xl"
                  >
                    ×
                  </button>
                </div>

                <form onSubmit={handleImageSearch} className="mb-6">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search for images..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="submit"
                      className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Search
                    </button>
                  </div>
                </form>

                {searchResults.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {searchResults.map((img, idx) => (
                      <div
                        key={idx}
                        className="cursor-pointer hover:opacity-75 transition-opacity"
                        onClick={() => handleSelectSearchedImage(img.largeImageURL)}
                      >
                        <img
                          src={img.previewURL}
                          alt={img.tags}
                          className="w-full h-48 object-cover rounded-lg shadow-md"
                        />
                        <p className="text-xs text-gray-600 mt-2 truncate">{img.tags}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
