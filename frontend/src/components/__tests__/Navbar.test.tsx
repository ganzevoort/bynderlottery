import { render, screen } from '@/lib/test-utils';
import Navbar from '../Navbar';

// Mock the auth hook
jest.mock('../../lib/auth', () => {
  const actual = jest.requireActual('../../lib/auth');
  return {
    ...actual,
    useAuth: () => ({
      user: null,
      logout: jest.fn(),
    }),
  };
});

describe('Navbar', () => {
  it('renders the lottery logo and brand name', () => {
    render(<Navbar />);

    expect(screen.getByText('Lottery')).toBeInTheDocument();
    expect(screen.getByText('Win Big!')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(<Navbar />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Open Draws')).toBeInTheDocument();
    expect(screen.getByText('Past Results')).toBeInTheDocument();
  });

  it('shows sign in link when user is not authenticated', () => {
    render(<Navbar />);

    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.queryByText('Profile')).not.toBeInTheDocument();
  });

  it('shows My Ballots when user is authenticated', () => {
    // Override the mock for this test
    const mockUseAuth = jest.fn().mockReturnValue({
      user: { id: 1, email: 'test@example.com', name: 'Test User' },
      logout: jest.fn(),
    });

    // Temporarily replace the mock
    const authModule = require('../../lib/auth');
    const originalUseAuth = authModule.useAuth;
    authModule.useAuth = mockUseAuth;

    render(<Navbar />);

    expect(screen.getByText('My Ballots')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();

    // Restore original mock
    authModule.useAuth = originalUseAuth;
  });
});
