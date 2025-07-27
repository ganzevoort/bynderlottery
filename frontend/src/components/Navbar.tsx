'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Euro, Menu, X, User, LogOut, Settings, Sparkles } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

export default function Navbar() {
    const { user, loading, logout } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [userDropdownOpen, setUserDropdownOpen] = useState(false);
    const router = useRouter();

    const handleLogout = async () => {
        try {
            await logout();
            toast.success('Successfully logged out');
            router.push('/auth/signin');
        } catch (error) {
            toast.error('Failed to log out');
        }
    };

    return (
        <nav style={{
            position: 'sticky',
            top: 0,
            zIndex: 50,
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(12px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}>
            <div style={{
                maxWidth: '1280px',
                margin: '0 auto',
                padding: '0 16px'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    height: '64px'
                }}>
                    {/* Logo and brand */}
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ position: 'relative' }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    background: 'linear-gradient(to bottom right, #22c55e, #16a34a)',
                                    borderRadius: '50%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                    transition: 'all 0.3s ease'
                                }}>
                                    <Euro style={{ width: '24px', height: '24px', color: 'white' }} />
                                </div>
                                <div style={{
                                    position: 'absolute',
                                    top: '-4px',
                                    right: '-4px',
                                    width: '16px',
                                    height: '16px',
                                    backgroundColor: '#fbbf24',
                                    borderRadius: '50%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <Sparkles style={{ width: '8px', height: '8px', color: '#92400e' }} />
                                </div>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <span style={{
                                    fontSize: '20px',
                                    fontWeight: 'bold',
                                    background: 'linear-gradient(to right, #16a34a, #2563eb)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    backgroundClip: 'text'
                                }}>Lottery</span>
                                <span style={{ fontSize: '12px', color: '#6b7280', marginTop: '-4px' }}>Win Big!</span>
                            </div>
                        </Link>
                    </div>

                    {/* Desktop navigation - hidden on mobile, visible on larger screens */}
                    <div style={{ alignItems: 'center', gap: '32px' }} className="desktop-nav">
                        <Link
                            href="/"
                            style={{
                                color: '#374151',
                                padding: '8px 12px',
                                borderRadius: '6px',
                                fontSize: '14px',
                                fontWeight: '500',
                                transition: 'all 0.2s ease',
                                textDecoration: 'none'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                                e.currentTarget.style.backgroundColor = '#f0fdf4';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                                e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                        >
                            Home
                        </Link>
                        <Link
                            href="/draws"
                            style={{
                                color: '#374151',
                                padding: '8px 12px',
                                borderRadius: '6px',
                                fontSize: '14px',
                                fontWeight: '500',
                                transition: 'all 0.2s ease',
                                textDecoration: 'none'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                                e.currentTarget.style.backgroundColor = '#f0fdf4';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                                e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                        >
                            Open Draws
                        </Link>
                        <Link
                            href="/draws/closed"
                            style={{
                                color: '#374151',
                                padding: '8px 12px',
                                borderRadius: '6px',
                                fontSize: '14px',
                                fontWeight: '500',
                                transition: 'all 0.2s ease',
                                textDecoration: 'none'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                                e.currentTarget.style.backgroundColor = '#f0fdf4';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                                e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                        >
                            Past Results
                        </Link>

                        {user ? (
                            <>
                                <Link
                                    href="/my-ballots"
                                    style={{
                                        color: '#374151',
                                        padding: '8px 12px',
                                        borderRadius: '6px',
                                        fontSize: '14px',
                                        fontWeight: '500',
                                        transition: 'all 0.2s ease',
                                        textDecoration: 'none'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#16a34a';
                                        e.currentTarget.style.backgroundColor = '#f0fdf4';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#374151';
                                        e.currentTarget.style.backgroundColor = 'transparent';
                                    }}
                                >
                                    My Ballots
                                </Link>
                                <div style={{ position: 'relative' }}>
                                    <button
                                        data-testid="user-menu"
                                        onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px',
                                            color: '#374151',
                                            padding: '8px 12px',
                                            borderRadius: '6px',
                                            fontSize: '14px',
                                            fontWeight: '500',
                                            transition: 'all 0.2s ease',
                                            border: 'none',
                                            background: 'transparent',
                                            cursor: 'pointer'
                                        }}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.color = '#16a34a';
                                            e.currentTarget.style.backgroundColor = '#f0fdf4';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.color = '#374151';
                                            e.currentTarget.style.backgroundColor = 'transparent';
                                        }}
                                    >
                                        <div style={{
                                            width: '32px',
                                            height: '32px',
                                            background: 'linear-gradient(to bottom right, #22c55e, #16a34a)',
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            <User style={{ width: '16px', height: '16px', color: 'white' }} />
                                        </div>
                                        <span>{user.name}</span>
                                    </button>

                                    {/* User dropdown menu */}
                                    {userDropdownOpen && (
                                        <div style={{
                                            position: 'absolute',
                                            top: '100%',
                                            right: '0',
                                            marginTop: '8px',
                                            background: 'white',
                                            borderRadius: '8px',
                                            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                                            border: '1px solid rgba(0, 0, 0, 0.1)',
                                            minWidth: '200px',
                                            zIndex: 1000
                                        }}>
                                            <div style={{ padding: '8px 0' }}>
                                                <Link
                                                    href="/profile"
                                                    style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '8px',
                                                        padding: '8px 16px',
                                                        color: '#374151',
                                                        textDecoration: 'none',
                                                        fontSize: '14px',
                                                        transition: 'all 0.2s ease'
                                                    }}
                                                    onMouseEnter={(e) => {
                                                        e.currentTarget.style.backgroundColor = '#f0fdf4';
                                                    }}
                                                    onMouseLeave={(e) => {
                                                        e.currentTarget.style.backgroundColor = 'transparent';
                                                    }}
                                                >
                                                    <Settings style={{ width: '16px', height: '16px' }} />
                                                    Profile Settings
                                                </Link>
                                                <button
                                                    data-testid="sign-out"
                                                    onClick={handleLogout}
                                                    style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '8px',
                                                        padding: '8px 16px',
                                                        color: '#ef4444',
                                                        background: 'transparent',
                                                        border: 'none',
                                                        width: '100%',
                                                        textAlign: 'left',
                                                        fontSize: '14px',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.2s ease'
                                                    }}
                                                    onMouseEnter={(e) => {
                                                        e.currentTarget.style.backgroundColor = '#fef2f2';
                                                    }}
                                                    onMouseLeave={(e) => {
                                                        e.currentTarget.style.backgroundColor = 'transparent';
                                                    }}
                                                >
                                                    <LogOut style={{ width: '16px', height: '16px' }} />
                                                    Sign Out
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <Link
                                    href="/auth/signin"
                                    style={{
                                        color: '#374151',
                                        padding: '8px 12px',
                                        borderRadius: '6px',
                                        fontSize: '14px',
                                        fontWeight: '500',
                                        transition: 'all 0.2s ease',
                                        textDecoration: 'none'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#16a34a';
                                        e.currentTarget.style.backgroundColor = '#f0fdf4';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#374151';
                                        e.currentTarget.style.backgroundColor = 'transparent';
                                    }}
                                >
                                    Sign In
                                </Link>
                                <Link
                                    href="/auth/signup"
                                    className="button-primary"
                                    style={{ fontSize: '14px', padding: '8px 16px' }}
                                >
                                    Sign Up
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile menu button - visible on mobile, hidden on larger screens */}
                    <div style={{ alignItems: 'center' }} className="mobile-nav">
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            style={{
                                color: '#374151',
                                padding: '8px',
                                borderRadius: '6px',
                                transition: 'color 0.2s ease',
                                border: 'none',
                                background: 'transparent',
                                cursor: 'pointer'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                            }}
                        >
                            {mobileMenuOpen ? (
                                <X style={{ width: '24px', height: '24px' }} />
                            ) : (
                                <Menu style={{ width: '24px', height: '24px' }} />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile menu */}
            {mobileMenuOpen && (
                <div style={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(12px)',
                    borderTop: '1px solid rgba(255, 255, 255, 0.2)',
                    animation: 'fadeIn 0.5s ease-out'
                }}>
                    <div style={{ padding: '8px 16px 12px' }}>
                        <Link
                            href="/"
                            style={{
                                display: 'block',
                                padding: '8px 12px',
                                color: '#374151',
                                borderRadius: '6px',
                                fontSize: '16px',
                                fontWeight: '500',
                                transition: 'color 0.2s ease',
                                textDecoration: 'none'
                            }}
                            onClick={() => setMobileMenuOpen(false)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                            }}
                        >
                            Home
                        </Link>
                        <Link
                            href="/draws"
                            style={{
                                display: 'block',
                                padding: '8px 12px',
                                color: '#374151',
                                borderRadius: '6px',
                                fontSize: '16px',
                                fontWeight: '500',
                                transition: 'color 0.2s ease',
                                textDecoration: 'none'
                            }}
                            onClick={() => setMobileMenuOpen(false)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                            }}
                        >
                            Open Draws
                        </Link>
                        <Link
                            href="/draws/closed"
                            style={{
                                display: 'block',
                                padding: '8px 12px',
                                color: '#374151',
                                borderRadius: '6px',
                                fontSize: '16px',
                                fontWeight: '500',
                                transition: 'color 0.2s ease',
                                textDecoration: 'none'
                            }}
                            onClick={() => setMobileMenuOpen(false)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#16a34a';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#374151';
                            }}
                        >
                            Past Results
                        </Link>

                        {user ? (
                            <>
                                <Link
                                    href="/my-ballots"
                                    style={{
                                        display: 'block',
                                        padding: '8px 12px',
                                        color: '#374151',
                                        borderRadius: '6px',
                                        fontSize: '16px',
                                        fontWeight: '500',
                                        transition: 'color 0.2s ease',
                                        textDecoration: 'none'
                                    }}
                                    onClick={() => setMobileMenuOpen(false)}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#16a34a';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#374151';
                                    }}
                                >
                                    My Ballots
                                </Link>
                                <Link
                                    href="/profile"
                                    style={{
                                        display: 'block',
                                        padding: '8px 12px',
                                        color: '#374151',
                                        borderRadius: '6px',
                                        fontSize: '16px',
                                        fontWeight: '500',
                                        transition: 'color 0.2s ease',
                                        textDecoration: 'none'
                                    }}
                                    onClick={() => setMobileMenuOpen(false)}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#16a34a';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#374151';
                                    }}
                                >
                                    Profile
                                </Link>
                                <button
                                    onClick={() => {
                                        handleLogout();
                                        setMobileMenuOpen(false);
                                    }}
                                    style={{
                                        display: 'block',
                                        width: '100%',
                                        textAlign: 'left',
                                        padding: '8px 12px',
                                        color: '#374151',
                                        borderRadius: '6px',
                                        fontSize: '16px',
                                        fontWeight: '500',
                                        transition: 'all 0.2s ease',
                                        border: 'none',
                                        background: 'transparent',
                                        cursor: 'pointer'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#dc2626';
                                        e.currentTarget.style.backgroundColor = '#fef2f2';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#374151';
                                        e.currentTarget.style.backgroundColor = 'transparent';
                                    }}
                                >
                                    Sign Out
                                </button>
                            </>
                        ) : (
                            <>
                                <Link
                                    href="/auth/signin"
                                    style={{
                                        display: 'block',
                                        padding: '8px 12px',
                                        color: '#374151',
                                        borderRadius: '6px',
                                        fontSize: '16px',
                                        fontWeight: '500',
                                        transition: 'color 0.2s ease',
                                        textDecoration: 'none'
                                    }}
                                    onClick={() => setMobileMenuOpen(false)}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#16a34a';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#374151';
                                    }}
                                >
                                    Sign In
                                </Link>
                                <Link
                                    href="/auth/signup"
                                    style={{
                                        display: 'block',
                                        padding: '8px 12px',
                                        background: 'linear-gradient(to right, #22c55e, #16a34a)',
                                        color: 'white',
                                        borderRadius: '6px',
                                        fontSize: '16px',
                                        fontWeight: '500',
                                        transition: 'all 0.2s ease',
                                        textDecoration: 'none'
                                    }}
                                    onClick={() => setMobileMenuOpen(false)}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = 'linear-gradient(to right, #16a34a, #15803d)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = 'linear-gradient(to right, #22c55e, #16a34a)';
                                    }}
                                >
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
} 
