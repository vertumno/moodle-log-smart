import { useState } from 'react'
import UploadZone from './components/UploadZone'
import ProgressBar from './components/ProgressBar'
import DownloadButton from './components/DownloadButton'

type AppState = 'idle' | 'processing' | 'completed' | 'error'

function App() {
  const [appState, setAppState] = useState<AppState>('idle')
  const [jobId, setJobId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Handler: Upload bem-sucedido → transição para processing
  const handleUploadSuccess = (newJobId: string) => {
    setJobId(newJobId)
    setAppState('processing')
    setError(null)
  }

  // Handler: Erro no upload → transição para error
  const handleUploadError = (err: { message: string }) => {
    setError(err.message)
    setAppState('error')
    setJobId(null)
  }

  // Handler: Processing completo → transição para completed
  const handleProcessingComplete = (completedJobId: string) => {
    setJobId(completedJobId)
    setAppState('completed')
    setError(null)
  }

  // Handler: Erro no processing → transição para error
  const handleProcessingError = (err: { message: string }) => {
    setError(err.message)
    setAppState('error')
  }

  // Handler: Download completo → reset para idle
  const handleDownloadComplete = () => {
    setAppState('idle')
    setJobId(null)
    setError(null)
  }

  // Handler: Retry após erro → reset para idle
  const handleRetry = () => {
    setAppState('idle')
    setJobId(null)
    setError(null)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900">MoodleLogSmart 🧠</h1>
        <p className="text-gray-600 mt-2">Transforme seus logs do Moodle</p>
        <p className="text-gray-500">em análises pedagógicas</p>
      </div>

      {/* Main Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        {/* Estado: idle ou upload - Mostrar UploadZone */}
        {(appState === 'idle') && (
          <UploadZone
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        )}

        {/* Estado: processing - Mostrar ProgressBar */}
        {appState === 'processing' && jobId && (
          <ProgressBar
            jobId={jobId}
            onComplete={handleProcessingComplete}
            onError={handleProcessingError}
          />
        )}

        {/* Estado: completed - Mostrar DownloadButton */}
        {appState === 'completed' && jobId && (
          <div className="text-center">
            <div className="text-5xl mb-4">✅</div>
            <p className="text-xl text-gray-900 mb-2 font-semibold">
              Processamento concluído!
            </p>
            <p className="text-gray-600 mb-6">
              Seu arquivo foi enriquecido com a Taxonomia de Bloom.
            </p>
            <DownloadButton
              jobId={jobId}
              onDownloadComplete={handleDownloadComplete}
            />
          </div>
        )}

        {/* Estado: error - Mostrar mensagem de erro */}
        {appState === 'error' && (
          <div className="text-center">
            <div className="text-5xl mb-4">❌</div>
            <p className="text-gray-900 mb-2 font-semibold">
              Erro ao processar
            </p>
            <p className="text-red-500 font-semibold mb-6">
              {error || 'Ocorreu um erro desconhecido'}
            </p>
            <button
              onClick={handleRetry}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 font-medium transition-colors"
            >
              Tentar Novamente
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="text-center mt-8 text-gray-500">
        <p>✨ Zero configuração necessária!</p>
        <p className="text-sm mt-2">Resultados: CSV enriquecido + XES + Bloom</p>
      </footer>
    </div>
  )
}

export default App
