# Frontend Testing Guide

This document explains the frontend testing setup and how to write tests for the lottery application.

## Testing Stack

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers for DOM testing
- **@testing-library/user-event**: User interaction simulation

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── __tests__/
│   │   │   └── Navbar.test.tsx
│   │   └── Navbar.tsx
│   ├── lib/
│   │   ├── __tests__/
│   │   │   ├── auth.test.ts
│   │   │   └── utils.test.ts
│   │   ├── auth.tsx
│   │   ├── utils.ts
│   │   └── test-utils.tsx
│   └── app/
│       └── __tests__/
│           └── (page tests)
├── jest.config.js
├── jest.setup.js
└── package.json
```

## Running Tests

### Local Development

```bash
# Run all tests
yarn test

# Run tests in watch mode
yarn test:watch

# Run tests with coverage
yarn test:coverage
```

### Using Docker

```bash
# Run all tests (includes frontend unit tests and linting)
./scripts/run-tests.sh
```

The script automatically runs frontend linting, unit tests, backend tests, and E2E tests.

## Writing Tests

### Component Tests

Use the custom `render` function from `@/lib/test-utils` which includes providers:

```tsx
import { render, screen } from '@/lib/test-utils';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Service Tests

Test API services with mocked axios:

```tsx
import { AuthService } from '@/lib/auth';
import { mockApiResponses } from '@/lib/test-utils';

// Mock axios
const mockAxios = require('axios');
const mockAxiosInstance = {
  post: jest.fn(),
  get: jest.fn(),
};

mockAxios.create.mockReturnValue(mockAxiosInstance);

describe('AuthService', () => {
  it('signs in successfully', async () => {
    mockAxiosInstance.post.mockResolvedValue({
      data: mockApiResponses.signin,
    });

    const result = await AuthService.signIn({
      email: 'test@example.com',
      password: 'password',
    });

    expect(result).toEqual(mockApiResponses.signin);
  });
});
```

### Utility Function Tests

Test pure functions directly:

```tsx
import { formatCurrency, validateCardNumber } from '@/lib/utils';

describe('formatCurrency', () => {
  it('formats positive numbers correctly', () => {
    expect(formatCurrency(1000)).toBe('€1,000.00');
  });
});

describe('validateCardNumber', () => {
  it('validates correct card numbers', () => {
    expect(validateCardNumber('4111111111111111')).toBe(true);
  });
});
```

## Test Utilities

### Mock Data

Use the mock data from `@/lib/test-utils`:

```tsx
import { mockUser, mockAccount, mockDraw } from '@/lib/test-utils';

// Use in tests
const user = mockUser;
const account = mockAccount;
```

### Custom Render Function

The custom render function includes:

- AuthProvider context
- All necessary providers
- Proper TypeScript support

### Mocking

Common mocks are set up in `jest.setup.js`:

- Next.js router
- react-hot-toast
- axios
- Browser APIs (ResizeObserver, matchMedia)

## Best Practices

1. **Test Behavior, Not Implementation**: Focus on what the user sees and does
2. **Use Semantic Queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
3. **Test Error States**: Don't just test happy paths
4. **Keep Tests Simple**: One assertion per test when possible
5. **Use Descriptive Names**: Test names should describe the behavior being tested

## Coverage

Tests should aim for:

- **Lines**: 70% minimum
- **Functions**: 70% minimum
- **Branches**: 70% minimum
- **Statements**: 70% minimum

## Common Patterns

### Testing Forms

```tsx
import { render, screen, fireEvent } from '@/lib/test-utils';
import userEvent from '@testing-library/user-event';

it('submits form with correct data', async () => {
  const user = userEvent.setup();
  render(<SignInForm />);

  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.type(screen.getByLabelText('Password'), 'password');
  await user.click(screen.getByRole('button', { name: 'Sign In' }));

  // Assert form submission
});
```

### Testing Async Operations

```tsx
it('loads data on mount', async () => {
  render(<DataComponent />);

  expect(screen.getByText('Loading...')).toBeInTheDocument();

  await screen.findByText('Data loaded');

  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
});
```

### Testing Error States

```tsx
it('shows error message on API failure', async () => {
  // Mock API to throw error
  mockAxiosInstance.get.mockRejectedValue(new Error('API Error'));

  render(<DataComponent />);

  await screen.findByText('Failed to load data');
});
```

## Troubleshooting

### Common Issues

1. **Provider Errors**: Make sure to use the custom `render` function
2. **Mock Issues**: Check that mocks are properly set up in `jest.setup.js`
3. **TypeScript Errors**: Ensure test files have `.test.tsx` or `.spec.tsx` extension
4. **Async Test Failures**: Use `waitFor` or `findBy` for async operations

### Debugging

```bash
# Run tests with verbose output
yarn test --verbose

# Run specific test file
yarn test Navbar.test.tsx

# Run tests with coverage
yarn test --coverage --watchAll=false
```
