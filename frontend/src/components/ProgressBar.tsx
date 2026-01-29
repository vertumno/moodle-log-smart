interface ProgressBarProps {
  progress: number
}

export default function ProgressBar({ progress }: ProgressBarProps) {
  const getStatusMessage = () => {
    if (progress < 20) return 'Detectando formato...'
    if (progress < 40) return 'Limpando dados...'
    if (progress < 60) return 'Enriquecendo com Bloom...'
    if (progress < 80) return 'Exportando resultados...'
    return 'Empacotando...'
  }

  return (
    <div className="space-y-4">
      <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
        <div
          className="bg-gradient-to-r from-blue-600 to-green-600 h-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      <div className="flex justify-between items-center">
        <p className="text-gray-700 font-medium">
          {getStatusMessage()}
        </p>
        <p className="text-2xl font-bold text-blue-600">
          {progress}%
        </p>
      </div>
    </div>
  )
}
