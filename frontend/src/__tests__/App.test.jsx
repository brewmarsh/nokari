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
  const linkElements = await screen.findAllByText(/login/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
