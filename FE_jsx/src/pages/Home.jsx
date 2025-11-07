import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Create Stunning Presentations with AI
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Generate professional PowerPoint presentations in seconds using artificial intelligence.
          Just enter a topic and let our AI do the rest.
        </p>
        <Link
          to="/generate"
          className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Get Started →
        </Link>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">AI-Powered Content</h3>
          <p className="text-gray-600">
            Leverage Claude and Groq AI to generate intelligent, well-structured presentation content
            tailored to your topic.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">🎨</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Beautiful Themes</h3>
          <p className="text-gray-600">
            Choose from 7 professional themes including Modern, Dark, Professional, Business, Academic,
            Minimal, and Creative.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">🖼️</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Smart Images</h3>
          <p className="text-gray-600">
            Automatically find and insert relevant royalty-free images from Pixabay with 5 suggestions
            per slide.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">✏️</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Live Editing</h3>
          <p className="text-gray-600">
            Edit slide titles, content, and swap images directly in the browser before downloading.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">📄</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Document Upload</h3>
          <p className="text-gray-600">
            Upload PDF or DOCX files to extract text and generate presentations from existing content.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-4xl mb-4">🎨</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Brand Colors</h3>
          <p className="text-gray-600">
            Customize presentations with your brand colors in RGB or hex format for consistent branding.
          </p>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 text-blue-600 w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              1
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Enter Topic</h4>
            <p className="text-sm text-gray-600">Provide a topic or upload a document</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 text-blue-600 w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              2
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">AI Generates</h4>
            <p className="text-sm text-gray-600">AI creates outline and content</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 text-blue-600 w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              3
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Edit & Refine</h4>
            <p className="text-sm text-gray-600">Customize slides and images</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 text-blue-600 w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
              4
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Download</h4>
            <p className="text-sm text-gray-600">Get your PPTX file ready</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-xl p-12 text-center text-white">
        <h2 className="text-3xl font-bold mb-4">Ready to Create Your First Presentation?</h2>
        <p className="text-xl mb-8 opacity-90">
          Join thousands of users creating professional presentations with AI
        </p>
        <Link
          to="/generate"
          className="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors"
        >
          Start Generating →
        </Link>
      </div>
    </div>
  )
}
