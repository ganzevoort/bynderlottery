import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { AuthProvider } from './auth';

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return <AuthProvider>{children}</AuthProvider>;
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';

// Override render method
export { customRender as render };

// Test data helpers
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  is_active: true,
};

export const mockAccount = {
  id: 1,
  user: mockUser,
  bankaccount: 'NL91ABNA0417164300',
  email_verified: true,
};

export const mockDraw = {
  id: 1,
  drawtype: {
    id: 1,
    name: 'Weekly Draw',
    is_active: true,
  },
  date: '2024-01-15T20:00:00Z',
  closed: null,
  prizes: [
    {
      id: 1,
      name: 'First Prize',
      amount: 1000,
      number: 1,
      drawtype: 1,
    },
  ],
  winner_count: 0,
  total_prize_amount: 1000,
};

export const mockBallot = {
  id: 1,
  draw: mockDraw,
  prize: null,
};

// Mock API responses
export const mockApiResponses = {
  signin: {
    message: 'Successfully signed in!',
  },
  signup: {
    message:
      'Account created successfully! Please check your email to verify your account.',
  },
  profile: mockAccount,
  draws: [mockDraw],
  ballots: {
    unassigned_ballots: [mockBallot],
    assigned_ballots: [],
    total_ballots: 1,
  },
};
