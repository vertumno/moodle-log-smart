import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ProgressBar from './ProgressBar';

// Mock fetch
global.fetch = vi.fn();

describe('ProgressBar', () => {
  const mockOnComplete = vi.fn();
  const mockOnError = vi.fn();
  const testJobId = 'test-job-123';

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('renders with initial processing state', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 10,
      }),
    });

    render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    expect(screen.getByText(/Detectando formato.../i)).toBeInTheDocument();
  });

  it('polls API immediately on mount', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 10,
      }),
    });

    render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`/api/status/${testJobId}`);
    });
  });

  it('updates progress correctly', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 45,
      }),
    });

    render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('45%')).toBeInTheDocument();
    });
  });

  it('shows correct status messages for different progress levels', async () => {
    const { rerender } = render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    // 0-20%: Detectando formato
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 15,
      }),
    });

    await waitFor(() => {
      expect(screen.getByText(/Detectando formato.../i)).toBeInTheDocument();
    });

    // 40-60%: Limpando dados
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 50,
      }),
    });

    rerender(<ProgressBar jobId={testJobId} onComplete={mockOnComplete} />);

    await waitFor(() => {
      expect(screen.getByText(/Limpando dados.../i)).toBeInTheDocument();
    });
  });

  it('calls onComplete when status is completed', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'completed',
        progress: 100,
      }),
    });

    render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledWith(testJobId);
    });

    await waitFor(() => {
      expect(screen.getByText(/Sucesso! Resultados prontos/i)).toBeInTheDocument();
    });
  });

  it('calls onError when status is failed', async () => {
    const errorMessage = 'Processing failed';
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'failed',
        progress: 50,
        error: errorMessage,
      }),
    });

    render(
      <ProgressBar
        jobId={testJobId}
        onComplete={mockOnComplete}
        onError={mockOnError}
      />
    );

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith({
        message: errorMessage,
      });
    });
  });

  it('stops polling when status becomes completed', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'completed',
        progress: 100,
      }),
    });

    render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    // Clear mock calls
    (global.fetch as any).mockClear();

    // Advance timer by 5 seconds (default poll interval)
    vi.advanceTimersByTime(5000);

    // Should not poll again after completion
    await waitFor(() => {
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  it('stops polling when status becomes failed', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'failed',
        progress: 50,
        error: 'Test error',
      }),
    });

    render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    // Clear mock calls
    (global.fetch as any).mockClear();

    // Advance timer
    vi.advanceTimersByTime(5000);

    // Should not poll again after failure
    await waitFor(() => {
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  it('handles 404 error gracefully', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Job not found' }),
    });

    render(
      <ProgressBar
        jobId={testJobId}
        onComplete={mockOnComplete}
        onError={mockOnError}
      />
    );

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith({
        message: 'Job não encontrado',
      });
    });
  });

  it('cleans up interval on unmount', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 50,
      }),
    });

    const { unmount } = render(
      <ProgressBar jobId={testJobId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    // Unmount component
    unmount();

    // Clear mock
    (global.fetch as any).mockClear();

    // Advance timer
    vi.advanceTimersByTime(5000);

    // Should not poll after unmount
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('uses custom poll interval', async () => {
    const customInterval = 2000;

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: testJobId,
        status: 'processing',
        progress: 30,
      }),
    });

    render(
      <ProgressBar
        jobId={testJobId}
        onComplete={mockOnComplete}
        pollInterval={customInterval}
      />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    // Clear mock
    (global.fetch as any).mockClear();

    // Advance by custom interval
    vi.advanceTimersByTime(customInterval);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });
});
