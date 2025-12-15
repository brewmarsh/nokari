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

// Mock api service
// Note: We cannot use top-level variables inside vi.mock callback due to hoisting.
// So we define the mocks inline or import them if needed.
// Alternatively, we can use `vi.importActual` to mock parts.
// But here, we just need to control the `get` method.

const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('../services/api', () => ({
  default: {
    get: (...args) => mockGet(...args),
    post: (...args) => mockPost(...args)
  },
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

describe('Jobs Component Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders error message when fetching jobs fails', async () => {
    // Simulate an error when fetching jobs via API
    const mockError = new Error('Missing or insufficient permissions');
    mockGet.mockRejectedValue(mockError);

    await act(async () => {
        render(<Jobs preferences={[]} />);
    });

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText(/Error: Missing or insufficient permissions/i)).toBeInTheDocument();
    });
  });
});
