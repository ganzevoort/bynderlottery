'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface VerifyEmailPageProps {
  params: Promise<{
    token: string;
  }>;
}

export default function VerifyEmailPage({ params }: VerifyEmailPageProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>(
    'loading'
  );
  const [message, setMessage] = useState('');
  const [, setToken] = useState<string>('');
  const router = useRouter();

  useEffect(() => {
    const initializePage = async () => {
      const resolvedParams = await params;
      setToken(resolvedParams.token);

      const verifyEmail = async () => {
        try {
          const response = await fetch(
            `/api/accounts/verify-email/${resolvedParams.token}/`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
            }
          );

          if (response.ok) {
            setStatus('success');
            setMessage('Email verified successfully! You can now sign in.');
            // Redirect to signin after 3 seconds
            setTimeout(() => {
              router.push('/auth/signin');
            }, 3000);
          } else {
            const errorData = await response.json();
            setStatus('error');
            setMessage(errorData.error || 'Invalid verification link.');
          }
        } catch {
          setStatus('error');
          setMessage('An error occurred while verifying your email.');
        }
      };

      if (resolvedParams.token) {
        verifyEmail();
      }
    };

    initializePage();
  }, [params, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Email Verification
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Verifying your email address...
          </p>
        </div>

        <div className="mt-8 space-y-6">
          {status === 'loading' && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Verifying your email...</p>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                Success!
              </h3>
              <p className="mt-2 text-sm text-gray-600">{message}</p>
              <p className="mt-2 text-xs text-gray-500">
                Redirecting to sign in...
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg
                  className="h-6 w-6 text-red-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                Verification Failed
              </h3>
              <p className="mt-2 text-sm text-gray-600">{message}</p>
            </div>
          )}

          <div className="text-center">
            <Link
              href="/auth/signin"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Go to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
