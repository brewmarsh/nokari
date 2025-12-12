import { vi, describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import React from 'react';
import Jobs from '../components/Jobs';

// Mock Dependencies
vi.mock('../firebaseConfig', () => ({
  db: {},
  auth: { currentUser: { uid: 'test-user' } },
}));

vi.mock('firebase/firestore', () => ({
  collection: vi.fn(),
  query: vi.fn(),
  where: vi.fn(),
  getDocs: vi.fn(),
  doc: vi.fn(),
  setDoc: vi.fn(),
  orderBy: vi.fn(),
  limit: vi.fn(),
  startAfter: vi.fn(),
}));

vi.mock('../services/api', () => ({
  default: { post: vi.fn() },
}));

vi.mock('../hooks/useDebounce', () => ({
  default: (value) => value,
}));

// Mock Child Components to simplify testing
vi.mock('../components/JobCard', () => ({
  default: () => <div data-testid="job-card">Job Card</div>,
}));

vi.mock('../components/JobFilters', () => ({
  default: () => <div data-testid="job-filters">Job Filters</div>,
}));

import { getDocs } from 'firebase/firestore';

describe('Jobs Component Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders error message when fetching jobs fails', async () => {
    // Simulate an error when fetching jobs
    const mockError = new Error('Missing or insufficient permissions');
    vi.mocked(getDocs).mockRejectedValue(mockError);

    await act(async () => {
        render(<Jobs preferences={[]} />);
    });

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText(/Error: Missing or insufficient permissions/i)).toBeInTheDocument();
    });

    // Verify hooks order did not cause a crash (if it crashed, the test would fail or not reach this point)
    // The previous bug caused "Rendered fewer hooks than expected" which crashes React.
    // By successfully rendering the error message, we prove the fix works.
  });
});
