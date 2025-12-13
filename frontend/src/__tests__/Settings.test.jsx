import { vi, describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import * as firebaseFirestore from 'firebase/firestore';
import api from '../services/api';
import Settings from '../components/Settings';

// Mock dependencies
vi.mock('../services/api', () => ({
  default: {
    patch: vi.fn(),
  },
}));

vi.mock('../firebaseConfig', () => ({
  db: {},
}));

vi.mock('firebase/firestore', () => ({
  doc: vi.fn(),
  updateDoc: vi.fn(),
}));

describe('Settings Component', () => {
  const mockUser = {
    uid: 'test-uid',
    preferred_work_arrangement: ['remote'],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with user preferences', () => {
    render(<Settings user={mockUser} />);

    const remoteCheckbox = screen.getByLabelText(/Remote/i);
    const hybridCheckbox = screen.getByLabelText(/Hybrid/i);

    expect(remoteCheckbox).toBeChecked();
    expect(hybridCheckbox).not.toBeChecked();
  });

  it('updates preferences when checkboxes are toggled', () => {
    render(<Settings user={mockUser} />);

    const hybridCheckbox = screen.getByLabelText(/Hybrid/i);
    fireEvent.click(hybridCheckbox);
    expect(hybridCheckbox).toBeChecked();

    const remoteCheckbox = screen.getByLabelText(/Remote/i);
    fireEvent.click(remoteCheckbox);
    expect(remoteCheckbox).not.toBeChecked();
  });

  it('saves settings to Firestore and API', async () => {
    vi.mocked(api.patch).mockResolvedValue({});
    vi.mocked(firebaseFirestore.updateDoc).mockResolvedValue();

    render(<Settings user={mockUser} />);

    // Add Hybrid, Remove Remote -> Result: [Hybrid]
    fireEvent.click(screen.getByLabelText(/Hybrid/i));
    fireEvent.click(screen.getByLabelText(/Remote/i));

    fireEvent.click(screen.getByText(/Save Settings/i));

    expect(screen.getByText(/Saving.../i)).toBeInTheDocument();

    await waitFor(() => {
        expect(screen.getByText(/Your settings have been saved/i)).toBeInTheDocument();
    });

    // Check Firestore update
    expect(firebaseFirestore.updateDoc).toHaveBeenCalledWith(
        undefined, // doc ref is undefined because doc() mock returns undefined
        { preferred_work_arrangement: ['hybrid'] }
    );

    // Check API update
    expect(api.patch).toHaveBeenCalledWith('/me/', { preferred_work_arrangement: ['hybrid'] });
  });

  it('handles backend error gracefully if Firestore succeeds', async () => {
    vi.mocked(firebaseFirestore.updateDoc).mockResolvedValue();
    vi.mocked(api.patch).mockRejectedValue(new Error('Backend failed'));

    render(<Settings user={mockUser} />);

    fireEvent.click(screen.getByText(/Save Settings/i));

    await waitFor(() => {
        // Should still show success
        expect(screen.getByText(/Your settings have been saved/i)).toBeInTheDocument();
    });
  });

  it('shows error if Firestore fails', async () => {
    vi.mocked(firebaseFirestore.updateDoc).mockRejectedValue(new Error('Firestore permission denied'));

    render(<Settings user={mockUser} />);

    fireEvent.click(screen.getByText(/Save Settings/i));

    await waitFor(() => {
        expect(screen.getByText(/Error: Firestore permission denied/i)).toBeInTheDocument();
    });
  });
});
