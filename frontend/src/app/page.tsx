'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Euro,
  Ticket,
  Trophy,
  Users,
  Calendar,
  ArrowRight,
  Star,
  Sparkles,
  Zap,
} from 'lucide-react';
import { LotteryService } from '@/lib/lottery';
import { useAuth } from '@/lib/auth';
import { LotteryStats } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function HomePage() {
  const [stats, setStats] = useState<LotteryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statsData = await LotteryService.getLotteryStats();
      setStats(statsData);
    } catch {
      toast.error('Failed to load lottery data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-green-200 border-t-green-600 rounded-full animate-spin"></div>
          <div
            className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-green-400 rounded-full animate-spin"
            style={{
              animationDirection: 'reverse',
              animationDuration: '1.5s',
            }}
          ></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-12 animate-fade-in">
      {/* Hero Section */}
      <div className="text-center py-16">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <div className="inline-flex items-center space-x-2 bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4" />
              <span>Trusted by thousands of players</span>
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Welcome to the{' '}
            <span className="gradient-text">Lottery System</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 mb-10 leading-relaxed max-w-3xl mx-auto">
            Experience the thrill of winning with our secure and fair lottery
            platform. Buy tickets, participate in draws, and win amazing
            prizes!
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            {user ? (
              <>
                <Link
                  href="/draws"
                  className="button-primary text-lg px-8 py-4 flex items-center justify-center group"
                >
                  <Ticket className="w-6 h-6 mr-3 group-hover:rotate-12 transition-transform" />
                  View Open Draws
                </Link>
                <Link
                  href="/my-ballots"
                  className="button-secondary text-lg px-8 py-4 flex items-center justify-center group"
                >
                  <Euro className="w-6 h-6 mr-3 group-hover:scale-110 transition-transform" />
                  My Ballots
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/auth/signup"
                  className="button-primary text-lg px-8 py-4 flex items-center justify-center group"
                >
                  <Users className="w-6 h-6 mr-3 group-hover:scale-110 transition-transform" />
                  Get Started
                </Link>
                <Link
                  href="/auth/signin"
                  className="button-secondary text-lg px-8 py-4 flex items-center justify-center group"
                >
                  Sign In
                </Link>
              </>
            )}
          </div>

          {/* Trust indicators */}
          <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Secure & Fair</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Instant Results</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>24/7 Support</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card card-hover">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-xl">
                <Calendar className="w-8 h-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  Total Draws
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.total_draws}
                </p>
              </div>
            </div>
          </div>

          <div className="card card-hover">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-xl">
                <Ticket className="w-8 h-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  Active Draws
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.active_draws}
                </p>
              </div>
            </div>
          </div>

          <div className="card card-hover">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-xl">
                <Trophy className="w-8 h-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  Prizes Awarded
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.total_prizes_awarded}
                </p>
              </div>
            </div>
          </div>

          <div className="card card-hover">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-xl">
                <Euro className="w-8 h-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  Total Winnings
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {formatCurrency(stats.total_amount_awarded)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="card card-hover text-center group">
          <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
            <Ticket className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">
            Buy Ballots
          </h3>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Purchase lottery tickets and participate in exciting draws with
            amazing prizes. Multiple prize categories available for every draw.
          </p>
          <Link
            href="/draws"
            className="inline-flex items-center text-green-600 hover:text-green-700 font-medium group/link"
          >
            View Draws{' '}
            <ArrowRight className="w-4 h-4 ml-2 group-hover/link:translate-x-1 transition-transform" />
          </Link>
        </div>

        <div className="card card-hover text-center group">
          <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
            <Trophy className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">
            Win Prizes
          </h3>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Check past results and see if you&apos;re a winner. Multiple prize
            categories with different winning chances and amounts.
          </p>
          <Link
            href="/draws/closed"
            className="inline-flex items-center text-green-600 hover:text-green-700 font-medium group/link"
          >
            Past Results{' '}
            <ArrowRight className="w-4 h-4 ml-2 group-hover/link:translate-x-1 transition-transform" />
          </Link>
        </div>

        <div className="card card-hover text-center group">
          <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
            <Zap className="w-8 h-8 text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">
            Secure Platform
          </h3>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Your account and transactions are protected with industry-standard
            security measures and encryption.
          </p>
          <Link
            href="/auth/signup"
            className="inline-flex items-center text-green-600 hover:text-green-700 font-medium group/link"
          >
            Join Now{' '}
            <ArrowRight className="w-4 h-4 ml-2 group-hover/link:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>

      {/* CTA Section */}
      {!user && (
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-green-700"></div>
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative bg-gradient-to-r from-green-600 to-green-700 rounded-3xl p-12 text-center text-white">
            <div className="max-w-3xl mx-auto">
              <div className="mb-6">
                <Star className="w-12 h-12 mx-auto text-yellow-300" />
              </div>
              <h2 className="text-4xl font-bold mb-4">
                Ready to Start Winning?
              </h2>
              <p className="text-xl mb-8 opacity-90 leading-relaxed">
                Create your account today and join thousands of players in our
                lottery system. Your next big win could be just a ticket away!
              </p>
              <Link
                href="/auth/signup"
                className="bg-white text-green-600 hover:bg-gray-100 px-10 py-4 rounded-xl font-semibold transition-all duration-200 inline-flex items-center shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <Users className="w-6 h-6 mr-3" />
                Create Account
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
