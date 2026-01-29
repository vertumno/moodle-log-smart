import { useState } from 'react'

interface DownloadButtonProps {
  jobId: string
}

export default function DownloadButton({ jobId }: DownloadButtonProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDownload = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/download/${jobId}`)

      if (!response.ok) {
        throw new Error('Erro ao baixar arquivo')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `results_${jobId}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button
        onClick={handleDownload}
        disabled={loading}
        className={`
          px-8 py-3 rounded-lg font-semibold text-white text-lg
          transition-all duration-200
          ${loading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700 active:scale-95'
          }
        `}
      >
        {loading ? '⏳ Baixando...' : '⬇️ Baixar Resultados (ZIP)'}
      </button>

      {error && (
        <p className="text-red-600 text-sm mt-2">
          {error}
        </p>
      )}

      <p className="text-gray-600 text-sm mt-4">
        ZIP contém: enriched_log.csv, enriched_log_bloom_only.csv, enriched_log.xes, enriched_log_bloom_only.xes
      </p>
    </div>
  )
}
