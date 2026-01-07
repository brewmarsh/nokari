import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import AdminJobs from '../components/AdminJobs';
import api from '../services/api';

// Mock API
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    delete: vi.fn(),
    post: vi.fn()
  }
}));

describe('AdminJobs Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation for window.confirm
    vi.spyOn(window, 'confirm').mockImplementation(() => true);
    // Mock window.alert
    vi.spyOn(window, 'alert').mockImplementation(() => {});
  });

  it('renders job rows with data-label attributes for responsiveness', async () => {
    // Mock response
    const mockJobs = [
      {
        job_id: '1',
        title: 'Test Job',
        company: 'Test Company',
        location: 'Remote',
        link: 'http://example.com',
        remote: true,
        hybrid: false,
        onsite: false,
        updated_at: '2023-01-01T00:00:00Z'
      }
    ];
    api.get.mockResolvedValue({ data: mockJobs });

    render(<AdminJobs />);

    await waitFor(() => {
        expect(screen.getByText('Test Job')).toBeInTheDocument();
    });

    // Verify data-label attributes exist
    const titleCell = screen.getByText('Test Job').closest('td');
    expect(titleCell).toHaveAttribute('data-label', 'Job Title');

    const companyCell = screen.getByText('Test Company').closest('td');
    expect(companyCell).toHaveAttribute('data-label', 'Company');
  });

  it('calls rescrape-all endpoint when "Rescrape All" is clicked and confirmed', async () => {
      api.get.mockResolvedValue({ data: [] });
      api.post.mockResolvedValue({ data: { message: 'Started' } });

      render(<AdminJobs />);

      await waitFor(() => {
          expect(screen.getByText('Admin - Job Postings')).toBeInTheDocument();
      });

      const rescrapeAllBtn = screen.getByText('Rescrape All');
      fireEvent.click(rescrapeAllBtn);

      expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining('rescrape ALL jobs'));
      expect(api.post).toHaveBeenCalledWith('/admin/jobs/rescrape-all/');

      await waitFor(() => {
          expect(window.alert).toHaveBeenCalledWith(expect.stringContaining('Background task started'));
      });
  });

  it('does not call rescrape-all endpoint when cancelled', async () => {
    api.get.mockResolvedValue({ data: [] });
    window.confirm.mockReturnValue(false);

    render(<AdminJobs />);

    await waitFor(() => {
        expect(screen.getByText('Admin - Job Postings')).toBeInTheDocument();
    });

    const rescrapeAllBtn = screen.getByText('Rescrape All');
    fireEvent.click(rescrapeAllBtn);

    expect(window.confirm).toHaveBeenCalled();
    expect(api.post).not.toHaveBeenCalledWith('/admin/jobs/rescrape-all/');
});
});
