import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function History() {
  const navigate = useNavigate()
  const [presentations, setPresentations] = useState([])

  useEffect(() => {
    // Load presentation history from localStorage
    const history = JSON.parse(localStorage.getItem('ppt_history') || '[]')
    setPresentations(history)
  }, [])

  const handleView = (pptId) => {
    navigate(`/editor/${pptId}`)
  }

  const handleDelete = (pptId) => {
    const updatedHistory = presentations.filter(p => p.id !== pptId)
    localStorage.setItem('ppt_history', JSON.stringify(updatedHistory))
    setPresentations(updatedHistory)
  }

  if (presentations.length === 0) {
    return (
      <div className="px-4 py-12">
        <div className="max-w-3xl mx-auto text-center">
          <div className="text-6xl mb-4">📊</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">No Presentations Yet</h1>
          <p className="text-gray-600 mb-8">
            You haven't created any presentations yet. Start by generating your first one!
          </p>
          <button
            onClick={() => navigate('/generate')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700"
          >
            Create Presentation
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Presentation History</h1>

        <div className="grid md:grid-cols-2 gap-6">
          {presentations.map((ppt) => (
            <div key={ppt.id} className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{ppt.topic}</h3>
              <div className="space-y-1 text-sm text-gray-600 mb-4">
                <p>Theme: <span className="font-semibold">{ppt.theme}</span></p>
                <p>Slides: <span className="font-semibold">{ppt.slides}</span></p>
                <p>Created: <span className="font-semibold">{new Date(ppt.created).toLocaleString()}</span></p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleView(ppt.id)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  View
                </button>
                <button
                  onClick={() => handleDelete(ppt.id)}
                  className="px-4 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
