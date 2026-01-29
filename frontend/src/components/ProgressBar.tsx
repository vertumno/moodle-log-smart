import { useState, useEffect, useCallback } from 'react';

interface ProgressBarProps {
  jobId: string;
  onComplete: (jobId: string) => void;
  onError?: (error: { message: string }) => void;
  pollInterval?: number;
}

interface JobStatus {
  job_id: string;
  status: 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string | null;
  created_at?: string;
  completed_at?: string | null;
}

export default function ProgressBar({
  jobId,
  onComplete,
  onError,
  pollInterval = 5000,
}: ProgressBarProps) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'processing' | 'completed' | 'failed'>('processing');
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  const getStatusMessage = (currentProgress: number, currentStatus: string): string => {
    if (currentStatus === 'completed') {
      return 'Sucesso! Resultados prontos para download';
    }

    if (currentStatus === 'failed') {
      return `Erro: ${error || 'Falha no processamento'}`;
    }

    if (currentProgress < 20) return 'Detectando formato...';
    if (currentProgress < 40) return 'Mapeando colunas...';
    if (currentProgress < 60) return 'Limpando dados...';
    if (currentProgress < 80) return 'Enriquecendo atividades...';
    if (currentProgress < 100) return 'Gerando resultados...';
    return 'Processando...';
  };

  const pollStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`/api/status/${jobId}`);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Job não encontrado');
        }
        throw new Error('Erro ao verificar status');
      }

      const data: JobStatus = await response.json();

      setProgress(data.progress);
      setStatus(data.status);

      if (data.status === 'completed') {
        setIsPolling(false);
        setProgress(100);
        if (onComplete) {
          onComplete(data.job_id);
        }
      } else if (data.status === 'failed') {
        setIsPolling(false);
        const errorMsg = data.error || 'Falha no processamento';
        setError(errorMsg);
        if (onError) {
          onError({ message: errorMsg });
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMsg);

      // Don't stop polling on network errors, retry
      // Only stop on job not found or failed status
      if (errorMsg.includes('não encontrado')) {
        setIsPolling(false);
        if (onError) {
          onError({ message: errorMsg });
        }
      }
    }
  }, [jobId, onComplete, onError]);

  useEffect(() => {
    if (!jobId || !isPolling) return;

    // Initial poll immediately
    pollStatus();

    // Setup polling interval
    const interval = setInterval(() => {
      if (isPolling) {
        pollStatus();
      }
    }, pollInterval);

    // Cleanup on unmount or when polling stops
    return () => {
      clearInterval(interval);
    };
  }, [jobId, isPolling, pollInterval, pollStatus]);

  // Stop polling when status changes to completed or failed
  useEffect(() => {
    if (status === 'completed' || status === 'failed') {
      setIsPolling(false);
    }
  }, [status]);

  const statusMessage = getStatusMessage(progress, status);

  return (
    <div className="w-full max-w-md mx-auto space-y-4">
      {/* Status message with spinner */}
      <div className="flex items-center space-x-2">
        {status === 'processing' && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
        )}
        {status === 'completed' && <span className="text-2xl">✅</span>}
        {status === 'failed' && <span className="text-2xl">❌</span>}
        <p
          className={`font-medium ${
            status === 'completed'
              ? 'text-green-600'
              : status === 'failed'
              ? 'text-red-600'
              : 'text-gray-700'
          }`}
        >
          {statusMessage}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            status === 'completed'
              ? 'bg-green-500'
              : status === 'failed'
              ? 'bg-red-500'
              : 'bg-blue-500'
          }`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {/* Progress percentage */}
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">Progresso</p>
        <p
          className={`text-2xl font-bold ${
            status === 'completed'
              ? 'text-green-600'
              : status === 'failed'
              ? 'text-red-600'
              : 'text-blue-600'
          }`}
        >
          {progress}%
        </p>
      </div>
    </div>
  );
}
