import { useState } from 'react'

export default function SlidePreview({ slide, slideIndex, onUpdate, onImageChange }) {
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [editedTitle, setEditedTitle] = useState(slide.title || '')
  const [editedBullets, setEditedBullets] = useState(slide.content || [])
  const [showImagePicker, setShowImagePicker] = useState(false)

  const handleTitleSave = () => {
    if (editedTitle !== slide.title) {
      onUpdate(slideIndex, { ...slide, title: editedTitle })
    }
    setIsEditingTitle(false)
  }

  const handleBulletChange = (bulletIndex, newValue) => {
    const newBullets = [...editedBullets]
    newBullets[bulletIndex] = newValue
    setEditedBullets(newBullets)
  }

  const handleBulletSave = (bulletIndex) => {
    if (JSON.stringify(editedBullets) !== JSON.stringify(slide.content)) {
      onUpdate(slideIndex, { ...slide, content: editedBullets })
    }
  }

  const handleImageSelect = (imageUrl) => {
    onImageChange(slideIndex, imageUrl)
    setShowImagePicker(false)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          {isEditingTitle ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <button
                onClick={handleTitleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Save
              </button>
              <button
                onClick={() => {
                  setEditedTitle(slide.title || '')
                  setIsEditingTitle(false)
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          ) : (
            <h3
              className="text-2xl font-bold text-gray-800 cursor-pointer hover:text-blue-600"
              onClick={() => setIsEditingTitle(true)}
            >
              {slide.title || 'Untitled Slide'}
            </h3>
          )}
        </div>
        <span className="text-sm text-gray-500 ml-4">Slide {slideIndex + 1}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Content Section */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Content:</h4>
          <ul className="space-y-2">
            {editedBullets.map((bullet, idx) => (
              <li key={idx} className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <input
                  type="text"
                  value={bullet}
                  onChange={(e) => handleBulletChange(idx, e.target.value)}
                  onBlur={() => handleBulletSave(idx)}
                  className="flex-1 px-2 py-1 border border-gray-200 rounded hover:border-blue-400 focus:outline-none focus:border-blue-500"
                />
              </li>
            ))}
          </ul>

          {slide.speaker_notes && (
            <div className="mt-4 p-3 bg-gray-50 rounded-md">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Speaker Notes:</h4>
              <p className="text-sm text-gray-600">{slide.speaker_notes}</p>
            </div>
          )}
        </div>

        {/* Image Section */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <h4 className="text-sm font-semibold text-gray-700">Image:</h4>
            <button
              onClick={() => setShowImagePicker(!showImagePicker)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Change Image
            </button>
          </div>

          {slide.image_path && (
            <img
              src={slide.image_path}
              alt={slide.title}
              className="w-full h-48 object-cover rounded-md shadow-sm"
            />
          )}

          {showImagePicker && slide.suggested_images && slide.suggested_images.length > 0 && (
            <div className="mt-4">
              <h5 className="text-sm font-semibold text-gray-700 mb-2">Suggested Images:</h5>
              <div className="grid grid-cols-2 gap-2">
                {slide.suggested_images.map((img, idx) => (
                  <img
                    key={idx}
                    src={img.previewURL || img.url}
                    alt={`Suggestion ${idx + 1}`}
                    className="w-full h-24 object-cover rounded cursor-pointer hover:ring-2 hover:ring-blue-500"
                    onClick={() => handleImageSelect(img.largeImageURL || img.url)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
