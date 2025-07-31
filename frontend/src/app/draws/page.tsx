'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Calendar, Euro, Users, ArrowRight, CheckCircle } from 'lucide-react';
import { LotteryService } from '@/lib/lottery';
import { Draw } from '@/lib/types';
import { formatCurrency, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function OpenDrawsPage() {
  const [draws, setDraws] = useState<Draw[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDraws();
  }, []);

  const loadDraws = async () => {
    try {
      const data = await LotteryService.getOpenDraws();
      setDraws(data);
    } catch {
      toast.error('Failed to load draws');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Open Draws</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Browse available lottery draws and assign your ballots to
          participate. Each draw has multiple prize categories with different
          winning chances.
        </p>
      </div>

      {draws.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Calendar className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Open Draws
          </h3>
          <p className="text-gray-600 mb-6">
            There are currently no open draws available. Check back later for
            new opportunities!
          </p>
          <Link
            href="/draws/closed"
            className="inline-flex items-center text-green-600 hover:text-green-700 font-medium"
          >
            View Past Results <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {draws.map((draw) => (
            <div
              key={draw.id}
              data-testid="draw-card"
              className="card card-hover overflow-hidden"
            >
              <div data-testid="draw-id" style={{ display: 'none' }}>
                {draw.id}
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {draw.drawtype.name}
                  </h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Open
                  </span>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span>{formatDate(draw.date)}</span>
                  </div>

                  <div className="flex items-center text-sm text-gray-600">
                    <Euro className="w-4 h-4 mr-2" />
                    <span>
                      Total Prize Pool:{' '}
                      {formatCurrency(draw.total_prize_amount)}
                    </span>
                  </div>

                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="w-4 h-4 mr-2" />
                    <span>{draw.prizes.length} Prize Categories</span>
                  </div>
                </div>

                <div className="space-y-2 mb-6">
                  <h4 className="text-sm font-medium text-gray-900">
                    Prize Categories:
                  </h4>
                  {draw.prizes.slice(0, 3).map((prize) => (
                    <div
                      key={prize.id}
                      className="flex justify-between text-sm"
                    >
                      <span className="text-gray-600">{prize.name}</span>
                      <span className="font-medium text-gray-900">
                        {formatCurrency(prize.amount)}
                      </span>
                    </div>
                  ))}
                  {draw.prizes.length > 3 && (
                    <p className="text-xs text-gray-500">
                      +{draw.prizes.length - 3} more prizes
                    </p>
                  )}
                </div>

                <div className="flex space-x-3">
                  <Link
                    href={`/draws/${draw.id}`}
                    className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors text-center"
                  >
                    View Details
                  </Link>
                  <Link
                    href="/my-ballots"
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors text-center"
                  >
                    Assign Ballots
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="text-center pt-8">
        <Link
          href="/draws/closed"
          className="inline-flex items-center text-green-600 hover:text-green-700 font-medium"
        >
          View Past Results and Winners <ArrowRight className="w-4 h-4 ml-1" />
        </Link>
      </div>
    </div>
  );
}
