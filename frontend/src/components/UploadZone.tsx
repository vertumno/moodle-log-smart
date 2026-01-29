import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface UploadZoneProps {
  onUpload: (file: File) => void
}

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
    },
    maxFiles: 1,
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-3 border-dashed rounded-xl p-12 text-center cursor-pointer
        transition-all duration-200
        ${isDragActive
          ? 'border-blue-600 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400 bg-gray-50'
        }
      `}
    >
      <input {...getInputProps()} />

      <div className="text-5xl mb-4">📁</div>

      <p className="text-xl font-semibold text-gray-900 mb-2">
        Arraste seu arquivo CSV aqui
      </p>

      <p className="text-gray-600 mb-4">
        ou clique para selecionar
      </p>

      <p className="text-sm text-gray-500">
        Arquivo CSV exportado diretamente do Moodle
      </p>
    </div>
  )
}
