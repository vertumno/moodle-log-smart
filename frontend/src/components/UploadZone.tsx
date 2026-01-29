import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface UploadZoneProps {
  onUploadSuccess: (jobId: string) => void;
  onUploadError?: (error: { message: string }) => void;
  disabled?: boolean;
}

export default function UploadZone({
  onUploadSuccess,
  onUploadError,
  disabled = false,
}: UploadZoneProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    // Check if file is CSV
    const isCSV =
      file.type === 'text/csv' ||
      file.type === 'application/vnd.ms-excel' ||
      file.name.toLowerCase().endsWith('.csv');

    if (!isCSV) {
      const errorMsg = 'Apenas arquivos .csv são permitidos';
      setError(errorMsg);
      if (onUploadError) {
        onUploadError({ message: errorMsg });
      }
      return false;
    }

    setError(null);
    return true;
  };

  const uploadFile = async (file: File): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao fazer upload');
      }

      const data = await response.json();

      // Success!
      setSuccess('Upload realizado com sucesso!');
      setFileName(file.name);

      // Auto-dismiss success message after 2 seconds
      setTimeout(() => setSuccess(null), 2000);

      // Call parent success callback
      if (onUploadSuccess && data.job_id) {
        onUploadSuccess(data.job_id);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMsg);

      if (onUploadError) {
        onUploadError({ message: errorMsg });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (disabled || isLoading) return;

      const file = acceptedFiles[0];
      if (!file) return;

      if (!validateFile(file)) {
        return;
      }

      await uploadFile(file);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [disabled, isLoading]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
    },
    maxFiles: 1,
    disabled: disabled || isLoading,
  });

  return (
    <div className="w-full max-w-md mx-auto">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
          ${disabled || isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          ${error ? 'border-red-400 bg-red-50' : ''}
          ${success ? 'border-green-400 bg-green-50' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center space-y-4">
          {/* Icon */}
          <div className="text-6xl">
            {isLoading ? '⏳' : '📁'}
          </div>

          {/* Main Text */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {isLoading
                ? 'Enviando arquivo...'
                : isDragActive
                ? 'Solte o arquivo aqui'
                : 'Arraste seu CSV aqui ou clique'}
            </h2>
            <p className="text-sm text-gray-600">
              Suporta logs exportados do Moodle
            </p>
          </div>

          {/* File name if uploaded */}
          {fileName && !isLoading && (
            <p className="text-sm text-gray-700 font-medium">
              📄 {fileName}
            </p>
          )}

          {/* Loading Spinner */}
          {isLoading && (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
              <span className="text-sm text-gray-600">Processando...</span>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="px-4 py-2 bg-green-100 border border-green-400 text-green-700 rounded">
              ✅ {success}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="px-4 py-2 bg-red-100 border border-red-400 text-red-700 rounded">
              ❌ {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
