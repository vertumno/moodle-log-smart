import { useState } from 'react'
import UploadZone from './components/UploadZone'
import ProgressBar from './components/ProgressBar'
import DownloadButton from './components/DownloadButton'

type ProcessingState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error'

function App() {
  const [state, setState] = useState<ProcessingState>('idle')
  const [progress, setProgress] = useState(0)
  const [jobId, setJobId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async (file: File) => {
    setState('uploading')
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Erro ao fazer upload')
      }

      const data = await response.json()
      setJobId(data.job_id)
      setState('processing')

      // Poll for status
      pollStatus(data.job_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      setState('error')
    }
  }

  const pollStatus = async (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/status/${jobId}`)
        const data = await response.json()

        setProgress(data.progress)

        if (data.status === 'completed') {
          setState('completed')
          clearInterval(interval)
        } else if (data.status === 'failed') {
          setError(data.error || 'Erro no processamento')
          setState('error')
          clearInterval(interval)
        }
      } catch (err) {
        console.error('Erro ao verificar status:', err)
        clearInterval(interval)
      }
    }, 1000)
  }

  const handleReset = () => {
    setState('idle')
    setProgress(0)
    setJobId(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              🎓 MoodleLogSmart
            </h1>
            <p className="text-lg text-gray-600">
              Transforme seus logs do Moodle em análises pedagógicas
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {state === 'idle' && (
              <>
                <p className="text-center text-gray-700 mb-8">
                  Envie seu arquivo CSV exportado do Moodle. Nós detectaremos o formato automaticamente.
                </p>
                <UploadZone onUpload={handleUpload} />
              </>
            )}

            {state === 'uploading' && (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Enviando arquivo...</p>
              </div>
            )}

            {state === 'processing' && (
              <div>
                <p className="text-center text-gray-700 mb-6">
                  Processando seu arquivo...
                </p>
                <ProgressBar progress={progress} />
              </div>
            )}

            {state === 'completed' && jobId && (
              <div className="text-center">
                <div className="text-5xl mb-4">✅</div>
                <p className="text-xl text-gray-900 mb-2">
                  Processamento concluído!
                </p>
                <p className="text-gray-600 mb-8">
                  Seu arquivo foi processado e enriquecido com a Taxonomia de Bloom.
                </p>
                <DownloadButton jobId={jobId} />
                <button
                  onClick={handleReset}
                  className="mt-4 px-6 py-2 text-blue-600 hover:text-blue-700 font-medium"
                >
                  Processar outro arquivo
                </button>
              </div>
            )}

            {state === 'error' && (
              <div>
                <div className="text-center text-5xl mb-4">❌</div>
                <p className="text-center text-gray-900 mb-2 font-medium">
                  Erro ao processar
                </p>
                <p className="text-center text-red-600 mb-8">
                  {error}
                </p>
                <div className="text-center">
                  <button
                    onClick={handleReset}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                  >
                    Tentar novamente
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="text-center mt-8 text-gray-600 text-sm">
            <p>MoodleLogSmart © 2026 • MIT License</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
