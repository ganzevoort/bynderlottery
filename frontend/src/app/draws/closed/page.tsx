'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Calendar, Euro, Trophy, Users, ArrowLeft } from 'lucide-react';
import { LotteryService } from '@/lib/lottery';
import { Draw } from '@/lib/types';
import { formatCurrency, formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function ClosedDrawsPage() {
    const [draws, setDraws] = useState<Draw[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDraws();
    }, []);

    const loadDraws = async () => {
        try {
            const data = await LotteryService.getClosedDraws();
            setDraws(data);
        } catch (error) {
            toast.error('Failed to load closed draws');
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
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Past Results</h1>
                    <p className="text-gray-600">
                        View completed draws and see the lucky winners.
                    </p>
                </div>
                <Link
                    href="/draws"
                    className="inline-flex items-center text-green-600 hover:text-green-700 font-medium"
                >
                    <ArrowLeft className="w-4 h-4 mr-1" />
                    Back to Open Draws
                </Link>
            </div>

            {draws.length === 0 ? (
                <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Trophy className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Closed Draws</h3>
                    <p className="text-gray-600 mb-6">
                        No draws have been completed yet. Check back later for results!
                    </p>
                    <Link
                        href="/draws"
                        className="inline-flex items-center text-green-600 hover:text-green-700 font-medium"
                    >
                        View Open Draws
                    </Link>
                </div>
            ) : (
                <div className="space-y-6">
                    {draws.map((draw) => (
                        <div key={draw.id} data-testid="closed-draw" className="card card-hover overflow-hidden">
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-xl font-semibold text-gray-900">{draw.drawtype.name}</h3>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                        Closed
                                    </span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                    <div className="flex items-center text-sm text-gray-600">
                                        <Calendar className="w-4 h-4 mr-2" />
                                        <span>{formatDate(draw.date)}</span>
                                    </div>

                                    <div className="flex items-center text-sm text-gray-600">
                                        <Euro className="w-4 h-4 mr-2" />
                                        <span>Total Prize Pool: {formatCurrency(draw.total_prize_amount)}</span>
                                    </div>

                                    <div className="flex items-center text-sm text-gray-600">
                                        <Users className="w-4 h-4 mr-2" />
                                        <span>{draw.winner_count} Winners</span>
                                    </div>
                                </div>

                                {draw.winners && draw.winners.length > 0 ? (
                                    <div>
                                        <h4 className="text-lg font-medium text-gray-900 mb-4">Winners</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                            {draw.winners.map((winner, index) => (
                                                <div key={index} className="card card-hover p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="font-medium text-gray-900">{winner.name}</span>
                                                        <Trophy className="w-5 h-5 text-yellow-600" />
                                                    </div>
                                                    <div className="text-sm text-gray-600">
                                                        <p className="font-medium">{winner.prize_name}</p>
                                                        <p className="text-green-600 font-semibold">
                                                            {formatCurrency(winner.prize_amount)}
                                                        </p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center py-4">
                                        <p className="text-gray-600">No winners for this draw.</p>
                                    </div>
                                )}

                                <div className="mt-6 pt-4 border-t border-gray-200">
                                    <h4 className="text-sm font-medium text-gray-900 mb-3">Prize Categories</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                        {draw.prizes.map((prize) => (
                                            <div key={prize.id} className="flex justify-between text-sm">
                                                <span className="text-gray-600">{prize.name}</span>
                                                <span className="font-medium text-gray-900">{formatCurrency(prize.amount)}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
} 
