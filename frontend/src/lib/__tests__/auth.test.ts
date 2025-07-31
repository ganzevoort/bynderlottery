import { AuthService } from '../auth';
import { mockApiResponses } from '../test-utils';

// Mock the api module inline
jest.mock('../api', () => {
  const mockApi = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  };
  return {
    __esModule: true,
    default: mockApi,
  };
});

// Import the mocked api
import api from '../api';

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('signIn', () => {
    it('successfully signs in a user', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };
      api.post.mockResolvedValue({ data: mockApiResponses.signin });

      const result = await AuthService.signIn(credentials);

      expect(api.post).toHaveBeenCalledWith('/accounts/signin/', credentials);
      expect(result).toEqual(mockApiResponses.signin);
    });

    it('handles sign in errors', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'wrongpassword',
      };
      const errorResponse = {
        response: { data: { message: 'Invalid credentials' } },
      };
      api.post.mockRejectedValue(errorResponse);

      await expect(AuthService.signIn(credentials)).rejects.toMatchObject(
        errorResponse
      );
    });
  });

  describe('signUp', () => {
    it('successfully signs up a user', async () => {
      const userData = {
        email: 'new@example.com',
        password1: 'password123',
        password2: 'password123',
        name: 'New User',
      };
      api.post.mockResolvedValue({ data: mockApiResponses.signup });

      const result = await AuthService.signUp(userData);

      expect(api.post).toHaveBeenCalledWith('/accounts/signup/', userData);
      expect(result).toEqual(mockApiResponses.signup);
    });

    it('handles sign up errors', async () => {
      const userData = {
        email: 'existing@example.com',
        password1: 'password123',
        password2: 'password123',
        name: 'Existing User',
      };
      const errorResponse = {
        response: { data: { message: 'Email already exists' } },
      };
      api.post.mockRejectedValue(errorResponse);

      await expect(AuthService.signUp(userData)).rejects.toMatchObject(
        errorResponse
      );
    });
  });

  describe('getProfile', () => {
    it('successfully retrieves user profile', async () => {
      api.get.mockResolvedValue({ data: mockApiResponses.profile });

      const result = await AuthService.getProfile();

      expect(api.get).toHaveBeenCalledWith('/accounts/profile/');
      expect(result).toEqual(mockApiResponses.profile);
    });

    it('handles profile retrieval errors', async () => {
      const errorResponse = { response: { status: 401 } };
      api.get.mockRejectedValue(errorResponse);

      await expect(AuthService.getProfile()).rejects.toMatchObject(
        errorResponse
      );
    });
  });

  describe('updateProfile', () => {
    it('successfully updates user profile', async () => {
      const profileData = {
        name: 'Updated Name',
        bankaccount: 'NL91ABNA0417164300',
      };
      const updatedProfile = {
        ...mockApiResponses.profile,
        user: { ...mockApiResponses.profile.user, name: 'Updated Name' },
      };
      api.put.mockResolvedValue({ data: updatedProfile });

      const result = await AuthService.updateProfile(profileData);

      expect(api.put).toHaveBeenCalledWith('/accounts/profile/', profileData);
      expect(result).toEqual(updatedProfile);
    });

    it('handles profile update errors', async () => {
      const profileData = { name: '', bankaccount: 'invalid' };
      const errorResponse = {
        response: { data: { message: 'Invalid data' } },
      };
      api.put.mockRejectedValue(errorResponse);

      await expect(
        AuthService.updateProfile(profileData)
      ).rejects.toMatchObject(errorResponse);
    });
  });

  describe('forgotPassword', () => {
    it('successfully sends password reset email', async () => {
      const email = 'test@example.com';
      const response = { message: 'Password reset email sent' };
      api.post.mockResolvedValue({ data: response });

      const result = await AuthService.forgotPassword({ email });

      expect(api.post).toHaveBeenCalledWith('/accounts/forgot-password/', {
        email,
      });
      expect(result).toEqual(response);
    });
  });

  describe('resetPassword', () => {
    it('successfully resets password', async () => {
      const token = 'valid-token';
      const passwordData = {
        password1: 'newpassword123',
        password2: 'newpassword123',
      };
      const response = { message: 'Password reset successfully' };
      api.post.mockResolvedValue({ data: response });

      const result = await AuthService.resetPassword(token, passwordData);

      expect(api.post).toHaveBeenCalledWith(
        `/accounts/reset-password/${token}/`,
        passwordData
      );
      expect(result).toEqual(response);
    });
  });

  describe('verifyEmail', () => {
    it('successfully verifies email', async () => {
      const token = 'valid-verification-token';
      const response = { message: 'Email verified successfully' };
      api.get.mockResolvedValue({ data: response });

      const result = await AuthService.verifyEmail(token);

      expect(api.get).toHaveBeenCalledWith(`/accounts/verify-email/${token}/`);
      expect(result).toEqual(response);
    });
  });

  describe('resendVerification', () => {
    it('successfully resends verification email', async () => {
      const email = 'test@example.com';
      const response = { message: 'Verification email sent' };
      api.post.mockResolvedValue({ data: response });

      const result = await AuthService.resendVerification(email);

      expect(api.post).toHaveBeenCalledWith('/accounts/resend-verification/', {
        email,
      });
      expect(result).toEqual(response);
    });
  });
});
