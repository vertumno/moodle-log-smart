import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DownloadButton from './DownloadButton';

// Mock fetch and DOM APIs
global.fetch = vi.fn();
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = vi.fn();

describe('DownloadButton', () => {
  const mockOnDownloadStart = vi.fn();
  const mockOnDownloadComplete = vi.fn();
  const mockOnDownloadError = vi.fn();
  const testJobId = 'test-job-123';

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('renders download button with correct text', () => {
    render(<DownloadButton jobId={testJobId} />);

    expect(screen.getByText(/Baixar Resultados \(ZIP\)/i)).toBeInTheDocument();
  });

  it('shows downloading state when clicked', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          setTimeout(
            () =>
              resolve({
                ok: true,
                blob: async () => new Blob(['test'], { type: 'application/zip' }),
                headers: new Headers(),
              }),
            100
          );
        })
    );

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(screen.getByText(/Baixando.../i)).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it('triggers download successfully', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    // Mock document methods
    const mockAppendChild = vi.spyOn(document.body, 'appendChild');
    const mockRemoveChild = vi.spyOn(document.body, 'removeChild');
    const mockClick = vi.fn();

    vi.spyOn(document, 'createElement').mockReturnValue({
      click: mockClick,
      style: {},
    } as any);

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`/api/download/${testJobId}`);
    });

    await waitFor(() => {
      expect(mockClick).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(mockAppendChild).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(mockRemoveChild).toHaveBeenCalled();
    });
  });

  it('shows success message after download', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
    } as any);

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Download iniciado!/i)).toBeInTheDocument();
    });
  });

  it('auto-dismisses success message after 3 seconds', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
    } as any);

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Download iniciado!/i)).toBeInTheDocument();
    });

    // Advance timers by 3 seconds
    vi.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(screen.queryByText(/Download iniciado!/i)).not.toBeInTheDocument();
    });
  });

  it('extracts filename from Content-Disposition header', async () => {
    const user = userEvent.setup({ delay: null });
    const testFilename = 'results_20240115.zip';

    const headers = new Headers();
    headers.set('Content-Disposition', `attachment; filename="${testFilename}"`);

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers,
    });

    let capturedFilename: string | undefined;
    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
      set download(value: string) {
        capturedFilename = value;
      },
    } as any);

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(capturedFilename).toBe(testFilename);
    });
  });

  it('uses fallback filename when header not present', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    let capturedFilename: string | undefined;
    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
      set download(value: string) {
        capturedFilename = value;
      },
    } as any);

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(capturedFilename).toMatch(/results_\d{8}_\d{6}\.zip/);
    });
  });

  it('shows error message on download failure', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Server error' }),
    });

    render(
      <DownloadButton
        jobId={testJobId}
        onDownloadError={mockOnDownloadError}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Server error/i)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockOnDownloadError).toHaveBeenCalledWith({
        message: 'Server error',
      });
    });
  });

  it('handles 404 error', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({}),
    });

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Arquivo não encontrado/i)).toBeInTheDocument();
    });
  });

  it('allows retry after error', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({}),
    });

    render(<DownloadButton jobId={testJobId} />);

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Erro ao baixar arquivo/i)).toBeInTheDocument();
    });

    // Click retry button
    const retryButton = screen.getByText(/Tentar novamente/i);

    (global.fetch as any).mockClear();
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
    } as any);

    await user.click(retryButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('calls onDownloadStart callback', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
    } as any);

    render(
      <DownloadButton
        jobId={testJobId}
        onDownloadStart={mockOnDownloadStart}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(mockOnDownloadStart).toHaveBeenCalled();
    });
  });

  it('calls onDownloadComplete callback', async () => {
    const user = userEvent.setup({ delay: null });

    (global.fetch as any).mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'application/zip' }),
      headers: new Headers(),
    });

    vi.spyOn(document, 'createElement').mockReturnValue({
      click: vi.fn(),
      style: {},
    } as any);

    render(
      <DownloadButton
        jobId={testJobId}
        onDownloadComplete={mockOnDownloadComplete}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);

    await waitFor(() => {
      expect(mockOnDownloadComplete).toHaveBeenCalled();
    });
  });

  it('disables button when disabled prop is true', () => {
    render(<DownloadButton jobId={testJobId} disabled={true} />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
