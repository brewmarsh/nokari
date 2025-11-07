import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Login from '../components/Login';
import { expect, test, vi } from 'vitest';

vi.mock('../services/api', () => ({
  api_unauthenticated: {
    get: vi.fn(() => Promise.resolve({ status: 200 })),
  },
}));

test('renders login form and version number', () => {
  render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );

  expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  expect(screen.getByText(/version/i)).toBeInTheDocument();
});
