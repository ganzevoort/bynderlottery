'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, Mail, CreditCard, Save, Eye, EyeOff } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { AuthService, useAuth } from '@/lib/auth';
import { ProfileForm } from '@/lib/types';
import toast from 'react-hot-toast';

export default function ProfilePage() {
    const { user, loading: authLoading } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [profile, setProfile] = useState<{
        user: { name: string; email: string };
        bankaccount: string;
        email_verified: boolean;
    } | null>(null);

    const router = useRouter();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<ProfileForm>();

    useEffect(() => {
        if (!authLoading) {
            loadProfile();
        }
    }, [authLoading, user]);

    const loadProfile = async () => {
        if (!user) {
            router.push('/auth/signin');
            return;
        }

        try {
            const data = await AuthService.getProfile();
            setProfile(data);
        } catch (error) {
            toast.error('Failed to load profile');
            router.push('/auth/signin');
        } finally {
            setLoading(false);
        }
    };

    const onSubmit = async (data: ProfileForm) => {
        setSaving(true);
        try {
            await AuthService.updateProfile(data);
            toast.success('Profile updated successfully!');
            loadProfile(); // Reload to get updated data
        } catch (error: any) {
            const message = error.response?.data?.message || 'Failed to update profile';
            toast.error(message);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            </div>
        );
    }

    // If user is null, don't render anything (will redirect in useEffect)
    if (!user) {
        return null;
    }

    if (!profile) {
        return null;
    }

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Profile Settings</h1>
                <p className="text-gray-600">
                    Manage your account information and preferences.
                </p>
            </div>

            <div className="card card-hover p-6">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    {/* Email Section */}
                    <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                            <Mail className="w-5 h-5 mr-2 text-gray-500" />
                            Email Information
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    value={profile.user.email}
                                    disabled
                                    className="input-field bg-gray-50 text-gray-500 cursor-not-allowed"
                                />
                                <p className="mt-1 text-sm text-gray-500">
                                    Email address cannot be changed
                                </p>
                            </div>

                            <div className="flex items-center">
                                <span className="text-sm text-gray-700">Email Verification:</span>
                                <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${profile.email_verified
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-red-100 text-red-800'
                                    }`}>
                                    {profile.email_verified ? 'Verified' : 'Not Verified'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Personal Information */}
                    <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                            <User className="w-5 h-5 mr-2 text-gray-500" />
                            Personal Information
                        </h3>
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                                Full Name
                            </label>
                            <input
                                {...register('name', {
                                    required: 'Full name is required',
                                    minLength: {
                                        value: 2,
                                        message: 'Name must be at least 2 characters',
                                    },
                                })}
                                id="name"
                                type="text"
                                defaultValue={profile.user.name}
                                className="input-field"
                                placeholder="Enter your full name"
                            />
                            {errors.name && (
                                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                            )}
                        </div>
                    </div>

                    {/* Bank Account Information */}
                    <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                            <CreditCard className="w-5 h-5 mr-2 text-gray-500" />
                            Bank Account Information
                        </h3>
                        <div>
                            <label htmlFor="bankaccount" className="block text-sm font-medium text-gray-700 mb-1">
                                Bank Account Number
                            </label>
                            <input
                                {...register('bankaccount', {
                                    maxLength: {
                                        value: 20,
                                        message: 'Bank account number must be 20 characters or less',
                                    },
                                })}
                                id="bankaccount"
                                type="text"
                                defaultValue={profile.bankaccount}
                                className="input-field"
                                placeholder="Enter your bank account number"
                            />
                            {errors.bankaccount && (
                                <p className="mt-1 text-sm text-red-600">{errors.bankaccount.message}</p>
                            )}
                            <p className="mt-1 text-sm text-gray-500">
                                This information is used for prize payouts
                            </p>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-end pt-6 border-t border-gray-200">
                        <button
                            type="submit"
                            disabled={saving}
                            className="button-primary flex items-center"
                        >
                            <Save className="w-4 h-4 mr-2" />
                            {saving ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Account Security Note */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-900 mb-2">Account Security</h4>
                <p className="text-sm text-blue-700">
                    Your account is protected with industry-standard security measures.
                    For password changes, please use the "Forgot Password" feature on the sign-in page.
                </p>
            </div>
        </div>
    );
} 
