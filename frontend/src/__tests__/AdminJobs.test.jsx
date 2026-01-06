import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
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
});
