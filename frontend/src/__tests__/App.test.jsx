import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { expect, test } from 'vitest';

test('renders login link', () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );
  const linkElements = screen.getAllByText(/login/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
