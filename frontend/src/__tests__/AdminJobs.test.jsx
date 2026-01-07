import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, beforeEach, test, expect } from 'vitest';
import AdminJobs from '../components/AdminJobs';
import api from '../services/api';

// Mock the API module
vi.mock('../services/api');

// Mock window.confirm
const mockConfirm = vi.fn();
window.confirm = mockConfirm;

// Mock window.alert
window.alert = vi.fn();

describe('AdminJobs Component', () => {
    const mockJobs = [
        {
            job_id: '1',
            title: 'Software Engineer',
            company: 'Tech Corp',
            location: 'San Francisco, CA', // Legacy field, might be present but ignored by new UI
            city: 'San Francisco',
            state: 'CA',
            country: 'USA',
            remote: false,
            hybrid: true,
            onsite: false,
            updated_at: '2023-10-27T10:00:00Z',
            link: 'http://example.com/job1'
        },
        {
            job_id: '2',
            title: 'Remote Dev',
            company: 'Remote First',
            city: null,
            state: null,
            country: null,
            remote: true,
            hybrid: false,
            onsite: false,
            updated_at: null,
            link: 'http://example.com/job2'
        }
    ];

    beforeEach(() => {
        vi.clearAllMocks();
        api.get.mockResolvedValue({ data: mockJobs });
    });

    test('renders job list with new columns correctly', async () => {
        render(<AdminJobs />);

        // Wait for loading to finish by waiting for the header or a job item
        await waitFor(() => {
             // We can wait for loading text to disappear
             expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
        });

        // Check for header
        expect(screen.getByText('Admin - Job Postings')).toBeInTheDocument();

        // Check for jobs
        expect(screen.getByText('Software Engineer')).toBeInTheDocument();

        // Check for new table headers
        expect(screen.getByText('City')).toBeInTheDocument();
        expect(screen.getByText('State')).toBeInTheDocument();
        expect(screen.getByText('Country')).toBeInTheDocument();

        // Ensure "Location" header is GONE
        expect(screen.queryByText('Location', { selector: 'th' })).not.toBeInTheDocument();

        // Check for data in new columns
        expect(screen.getByText('San Francisco')).toBeInTheDocument();
        expect(screen.getByText('CA')).toBeInTheDocument();
        expect(screen.getByText('USA')).toBeInTheDocument();

        // Check Remote/Hybrid/Onsite booleans rendered as Yes/No
        // Job 1 is Hybrid
        expect(screen.getAllByText('Yes').length).toBeGreaterThan(0);
        expect(screen.getAllByText('No').length).toBeGreaterThan(0);
    });

    test('handles delete action', async () => {
        render(<AdminJobs />);
        await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument());
        await waitFor(() => expect(screen.getByText('Software Engineer')).toBeInTheDocument());

        mockConfirm.mockReturnValue(true);
        api.delete.mockResolvedValue({});

        // Find delete buttons
        const deleteButtons = screen.getAllByText('Delete');
        fireEvent.click(deleteButtons[0]);

        await waitFor(() => {
            expect(api.delete).toHaveBeenCalledWith('/admin/jobs/1/');
        });

        // Should refetch
        expect(api.get).toHaveBeenCalledTimes(2);
    });

    test('handles rescrape action', async () => {
        render(<AdminJobs />);
        await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument());
        await waitFor(() => expect(screen.getByText('Software Engineer')).toBeInTheDocument());

        api.post.mockResolvedValue({});

        const rescrapeButtons = screen.getAllByText('Rescrape');
        fireEvent.click(rescrapeButtons[0]);

        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/admin/jobs/1/rescrape/');
        });

        expect(window.alert).toHaveBeenCalled();
    });

    test('renders job rows with data-label attributes for responsiveness', async () => {
        render(<AdminJobs />);
        await waitFor(() => expect(screen.queryByText('Loading...')).not.toBeInTheDocument());
        await waitFor(() => expect(screen.getByText('Software Engineer')).toBeInTheDocument());

        // Verify that the table cells have the correct data-label attributes for mobile view
        const cells = screen.getAllByRole('cell');

        // We can check if any cell has the attribute
        const cityCell = cells.find(cell => cell.textContent === 'San Francisco');
        expect(cityCell).toHaveAttribute('data-label', 'City');

        const countryCell = cells.find(cell => cell.textContent === 'USA');
        expect(countryCell).toHaveAttribute('data-label', 'Country');
    });
});
