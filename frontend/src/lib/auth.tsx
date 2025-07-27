'use client';

import api from './api';
import { User, SignUpForm, SignInForm, ForgotPasswordForm, ResetPasswordForm, ProfileForm } from './types';
import React, { createContext, useContext, useState, useEffect } from 'react';

export class AuthService {
    static async signUp(data: SignUpForm): Promise<{ user_id: number; message: string }> {
        const response = await api.post('/accounts/signup/', data);
        return response.data;
    }

    static async signIn(data: SignInForm): Promise<{ message: string }> {
        const response = await api.post('/accounts/signin/', data);
        return response.data;
    }

    static async signOut(): Promise<{ message: string }> {
        const response = await api.post('/accounts/signout/', {});
        return response.data;
    }

    static async verifyEmail(token: string): Promise<{ message: string }> {
        const response = await api.get(`/accounts/verify-email/${token}/`);
        return response.data;
    }

    static async resendVerification(email: string): Promise<{ message: string }> {
        const response = await api.post('/accounts/resend-verification/', { email });
        return response.data;
    }

    static async forgotPassword(data: ForgotPasswordForm): Promise<{ message: string }> {
        const response = await api.post('/accounts/forgot-password/', data);
        return response.data;
    }

    static async resetPassword(token: string, data: ResetPasswordForm): Promise<{ message: string }> {
        const response = await api.post(`/accounts/reset-password/${token}/`, data);
        return response.data;
    }

    static async getProfile(): Promise<{ user: User; bankaccount: string; email_verified: boolean }> {
        const response = await api.get('/accounts/profile/');
        return response.data;
    }

    static async updateProfile(data: ProfileForm): Promise<{ message: string }> {
        const response = await api.put('/accounts/profile/', data);
        return response.data;
    }

    static async checkAuth(): Promise<boolean> {
        try {
            await this.getProfile();
            return true;
        } catch (error: any) {
            // If it's a 401 or redirect error, user is not authenticated
            if (error.response?.status === 401 || error.response?.status === 302) {
                return false;
            }
            // For other errors, we can't determine auth status, so assume not authenticated
            return false;
        }
    }
}

// Auth context
interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (data: SignInForm) => Promise<{ message: string }>;
    logout: () => Promise<void>;
    loadUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const loadUser = async () => {
        try {
            const profile = await AuthService.getProfile();
            setUser(profile.user);
        } catch {
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (data: SignInForm) => {
        const result = await AuthService.signIn(data);
        await loadUser(); // Reload user data after login
        return result;
    };

    const logout = async () => {
        await AuthService.signOut();
        setUser(null);
    };

    useEffect(() => {
        loadUser();
    }, []);

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, loadUser }
        }>
            {children}
        </AuthContext.Provider>
    );
};

// Hook to use auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 
