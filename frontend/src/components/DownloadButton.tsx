import { useState } from 'react';

interface DownloadButtonProps {
  jobId: string;
  disabled?: boolean;
  onDownloadStart?: () => void;
  onDownloadComplete?: () => void;
  onDownloadError?: (error: { message: string }) => void;
}

export default function DownloadButton({
  jobId,
  disabled = false,
  onDownloadStart,
  onDownloadComplete,
  onDownloadError,
}: DownloadButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const getFilenameFromHeader = (contentDisposition: string | null): string => {
    if (!contentDisposition) {
      return generateFallbackFilename();
    }

    // Try to extract filename from Content-Disposition header
    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
    if (filenameMatch && filenameMatch[1]) {
      return filenameMatch[1];
    }

    return generateFallbackFilename();
  };

  const generateFallbackFilename = (): string => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `results_${year}${month}${day}_${hours}${minutes}${seconds}.zip`;
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);
    setSuccess(null);

    if (onDownloadStart) {
      onDownloadStart();
    }

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/download/${jobId}`);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Arquivo não encontrado');
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao baixar arquivo');
      }

      // Get blob from response
      const blob = await response.blob();

      // Extract filename from header or use fallback
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = getFilenameFromHeader(contentDisposition);

      // Create blob URL
      const url = window.URL.createObjectURL(blob);

      // Create invisible <a> element
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.style.display = 'none';

      // Append to body, trigger click, cleanup
      document.body.appendChild(a);
      a.click();

      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      // Show success message
      setSuccess('Download iniciado!');

      // Auto-dismiss after 3 seconds
      setTimeout(() => setSuccess(null), 3000);

      if (onDownloadComplete) {
        onDownloadComplete();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMsg);

      if (onDownloadError) {
        onDownloadError({ message: errorMsg });
      }
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <button
        onClick={handleDownload}
        disabled={disabled || isDownloading}
        className={`
          w-full px-8 py-3 rounded-lg font-semibold text-white text-lg
          transition-all duration-200
          ${
            disabled || isDownloading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 active:scale-95'
          }
        `}
      >
        {isDownloading ? '⏳ Baixando...' : '⬇️ Baixar Resultados (ZIP)'}
      </button>

      {/* Success message */}
      {success && (
        <div className="mt-4 px-4 py-2 bg-green-100 border border-green-400 text-green-700 rounded">
          ✅ {success}
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="mt-4 px-4 py-2 bg-red-100 border border-red-400 text-red-700 rounded">
          ❌ {error}
          <button
            onClick={handleDownload}
            className="ml-2 underline hover:no-underline"
          >
            Tentar novamente
          </button>
        </div>
      )}

      {/* Info text */}
      <p className="text-gray-600 text-sm mt-4 text-center">
        ZIP contém: CSV enriquecido + XES + Bloom
      </p>
    </div>
  );
}
