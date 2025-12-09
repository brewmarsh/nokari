import { vi } from 'vitest';

// Mock Firebase
vi.mock('../firebaseConfig', () => ({
  auth: {
    currentUser: null,
    onAuthStateChanged: vi.fn(),
    signOut: vi.fn(),
  },
  db: {
    collection: vi.fn(),
    doc: vi.fn(),
    getDoc: vi.fn(),
  },
  storage: {},
  initializationError: null,
}));

// Mock Firebase auth functions
vi.mock('firebase/auth', () => ({
  onAuthStateChanged: vi.fn((auth, callback) => {
    callback(null); // Simulate no user logged in
    return () => {}; // Return unsubscribe function
  }),
  signOut: vi.fn(),
}));

// Mock Firestore functions
vi.mock('firebase/firestore', () => ({
  doc: vi.fn(),
  getDoc: vi.fn(),
  collection: vi.fn(),
}));

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { expect, test } from 'vitest';

test('renders login link', async () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );
  // With code splitting, we might need to wait for the lazy loaded Login component?
  // But App.jsx renders Navigation immediately which has Login link.

  const linkElements = await screen.findAllByText(/login/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
