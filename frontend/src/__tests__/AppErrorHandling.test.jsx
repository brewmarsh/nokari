import { vi, describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import * as firebaseAuth from 'firebase/auth';
import * as firebaseFirestore from 'firebase/firestore';

// Mock Firebase Config
vi.mock('../firebaseConfig', () => ({
  auth: { currentUser: null },
  db: {},
  initializationError: null,
}));

// Mock Firebase Auth
vi.mock('firebase/auth', () => ({
  onAuthStateChanged: vi.fn(),
  signOut: vi.fn(),
}));

// Mock Firebase Firestore
vi.mock('firebase/firestore', () => ({
  doc: vi.fn(),
  getDoc: vi.fn(),
  collection: vi.fn(),
}));

import App from '../App';

describe('App Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('proceeds to dashboard when fetch user profile fails with permission denied', async () => {
    const mockUser = { uid: 'test-uid', email: 'test@example.com' };

    // Simulate user logged in
    vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation((auth, next, error) => {
        next(mockUser);
        return () => {};
    });

    // Simulate permission denied error on getDoc
    vi.mocked(firebaseFirestore.getDoc).mockRejectedValue({
        code: 'permission-denied',
        message: 'Missing or insufficient permissions.'
    });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // Should NOT show Loading Error
    await waitFor(() => {
        expect(screen.queryByText(/Loading Error/i)).not.toBeInTheDocument();
        // Should show Dashboard link (indicating user is logged in)
        expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    });
  });
});
