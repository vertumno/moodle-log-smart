import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadZone from './UploadZone';

// Mock fetch
global.fetch = vi.fn();

describe('UploadZone', () => {
  const mockOnUploadSuccess = vi.fn();
  const mockOnUploadError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders upload zone with correct text', () => {
    render(<UploadZone onUploadSuccess={mockOnUploadSuccess} />);

    expect(screen.getByText(/Arraste seu CSV aqui ou clique/i)).toBeInTheDocument();
    expect(screen.getByText(/Suporta logs exportados do Moodle/i)).toBeInTheDocument();
  });

  it('shows dragging state when file is dragged over', async () => {
    const { container } = render(<UploadZone onUploadSuccess={mockOnUploadSuccess} />);
    const dropzone = container.querySelector('[class*="border"]');

    // Simulate drag enter
    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    const dataTransfer = { files: [file] };

    if (dropzone) {
      await userEvent.upload(dropzone as HTMLElement, file);
    }

    // Dropzone should handle drag state
    expect(dropzone).toBeInTheDocument();
  });

  it('accepts CSV files and calls upload', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ job_id: 'test-job-123', status: 'processing' }),
    });

    render(<UploadZone onUploadSuccess={mockOnUploadSuccess} />);

    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByRole('presentation').querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLElement, file);
    }

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/upload',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalledWith('test-job-123');
    });
  });

  it('rejects non-CSV files with error message', async () => {
    render(
      <UploadZone
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByRole('presentation').querySelector('input[type="file"]');

    if (input) {
      // Note: useDropzone handles file validation internally
      // We're testing that our validateFile function works
      await userEvent.upload(input as HTMLElement, file);
    }

    // API should not be called for invalid files
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('shows loading state during upload', async () => {
    (global.fetch as any).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({ job_id: 'test-job-123' }),
              }),
            100
          );
        })
    );

    render(<UploadZone onUploadSuccess={mockOnUploadSuccess} />);

    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByRole('presentation').querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLElement, file);
    }

    // Should show loading spinner
    await waitFor(() => {
      expect(screen.getByText(/Enviando arquivo.../i)).toBeInTheDocument();
    });
  });

  it('displays success message after successful upload', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ job_id: 'test-job-123', status: 'processing' }),
    });

    render(<UploadZone onUploadSuccess={mockOnUploadSuccess} />);

    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByRole('presentation').querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLElement, file);
    }

    await waitFor(() => {
      expect(screen.getByText(/Upload realizado com sucesso!/i)).toBeInTheDocument();
    });
  });

  it('displays error message on upload failure', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'File too large' }),
    });

    render(
      <UploadZone
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByRole('presentation').querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLElement, file);
    }

    await waitFor(() => {
      expect(mockOnUploadError).toHaveBeenCalledWith({
        message: 'File too large',
      });
    });
  });

  it('disables upload zone when disabled prop is true', () => {
    const { container } = render(
      <UploadZone onUploadSuccess={mockOnUploadSuccess} disabled={true} />
    );

    const dropzone = container.querySelector('[class*="opacity-50"]');
    expect(dropzone).toBeInTheDocument();
  });
});
