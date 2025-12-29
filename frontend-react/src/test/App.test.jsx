import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App', () => {
    it('renders the header', () => {
        render(<App />);
        expect(screen.getByText('Lift Simulation Testbed')).toBeInTheDocument();
    });

    it('shows connecting status initially', () => {
        render(<App />);
        expect(screen.getByText(/Connecting/)).toBeInTheDocument();
    });
});
