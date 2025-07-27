'use client';

import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, Ticket, Euro, Calendar, Plus, CreditCard } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { LotteryService } from '@/lib/lottery';
import { UserBallots, BallotPurchaseForm, Draw } from '@/lib/types';
import { formatCurrency, formatDate, validateCardNumber, validateCVV, validateExpiry } from '@/lib/utils';
import toast from 'react-hot-toast';

interface BallotAssignmentForm {
    draw_id: number;
    quantity: number;
}

export default function MyBallotsPage() {
    const [ballots, setBallots] = useState<UserBallots | null>(null);
    const [draws, setDraws] = useState<Draw[]>([]);
    const [loading, setLoading] = useState(true);
    const [purchaseLoading, setPurchaseLoading] = useState(false);
    const [assignmentLoading, setAssignmentLoading] = useState(false);
    const [expandedSections, setExpandedSections] = useState({
        unassigned: false, // Default collapsed
        assigned: true,
        winning: true,
        purchase: false,
    });

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<BallotPurchaseForm>();

    const assignmentForm = useForm<BallotAssignmentForm>();

    useEffect(() => {
        loadBallots();
        loadDraws();
    }, []);

    const loadBallots = async () => {
        try {
            const data = await LotteryService.getUserBallots();
            setBallots(data);
        } catch (error) {
            toast.error('Failed to load ballots');
        } finally {
            setLoading(false);
        }
    };

    const loadDraws = async () => {
        try {
            const data = await LotteryService.getOpenDraws();
            setDraws(data);
        } catch (error) {
            console.error('Failed to load draws:', error);
        }
    };

    const toggleSection = (section: keyof typeof expandedSections) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section],
        }));
    };

    const onSubmitPurchase = async (data: BallotPurchaseForm) => {
        setPurchaseLoading(true);
        try {
            await LotteryService.purchaseBallots(data);
            toast.success(`Successfully purchased ${data.quantity} ballots!`);
            reset();
            loadBallots();
            setExpandedSections(prev => ({ ...prev, purchase: false }));
        } catch (error: any) {
            const message = error.response?.data?.message || 'Failed to purchase ballots';
            toast.error(message);
        } finally {
            setPurchaseLoading(false);
        }
    };



    const onSubmitAssignment = async (data: BallotAssignmentForm) => {
        setAssignmentLoading(true);
        try {
            console.log('Assigning ballots to draw:', data.draw_id, 'quantity:', data.quantity);

            // Get unassigned ballots
            const unassignedBallots = ballots?.unassigned_ballots || [];
            const ballotsToAssign = unassignedBallots.slice(0, data.quantity);

            // Assign each ballot
            for (const ballot of ballotsToAssign) {
                await LotteryService.assignBallot(ballot.id, { draw_id: data.draw_id, quantity: 1 });
            }

            const message = data.quantity === 1
                ? 'Ballot assigned successfully!'
                : `${data.quantity} ballots assigned successfully!`;
            toast.success(message);
            assignmentForm.reset();
            loadBallots();
        } catch (error: any) {
            console.error('Assignment error:', error);
            const message = error.response?.data?.error || 'Failed to assign ballots';
            toast.error(message);
        } finally {
            setAssignmentLoading(false);
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
                <h1 className="text-3xl font-bold text-gray-900 mb-4">My Ballots</h1>
                <p className="text-gray-600">
                    Manage your lottery tickets, purchase new ones, and assign them to draws.
                </p>
            </div>



            {/* Purchase Ballots Section */}
            <div className="card card-hover">
                <button
                    onClick={() => toggleSection('purchase')}
                    className="card-header-button"
                >
                    <div className="flex items-center">
                        <Plus className="w-5 h-5 text-green-600 mr-3" />
                        <h2 className="text-lg font-semibold text-gray-900">Purchase New Ballots</h2>
                    </div>
                    {expandedSections.purchase ? (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                    ) : (
                        <ChevronRight className="w-5 h-5 text-gray-500" />
                    )}
                </button>

                {expandedSections.purchase && (
                    <div className="px-6 pb-6">
                        <form onSubmit={handleSubmit(onSubmitPurchase)} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Number of Ballots
                                    </label>
                                    <input
                                        {...register('quantity', {
                                            required: 'Quantity is required',
                                            min: { value: 1, message: 'Minimum 1 ballot' },
                                            max: { value: 100, message: 'Maximum 100 ballots' },
                                        })}
                                        type="number"
                                        min="1"
                                        max="100"
                                        className="input-field"
                                        placeholder="Enter quantity"
                                    />
                                    {errors.quantity && (
                                        <p className="mt-1 text-sm text-red-600">{errors.quantity.message}</p>
                                    )}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Card Number
                                    </label>
                                    <input
                                        {...register('card_number', {
                                            required: 'Card number is required',
                                            validate: (value) => validateCardNumber(value) || 'Invalid card number',
                                        })}
                                        type="text"
                                        maxLength="19"
                                        className="input-field"
                                        placeholder="1234 5678 9012 3456"
                                    />
                                    {errors.card_number && (
                                        <p className="mt-1 text-sm text-red-600">{errors.card_number.message}</p>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Expiry Date
                                        </label>
                                        <div className="flex gap-2">
                                            <input
                                                {...register('expiry_month', {
                                                    required: 'Expiry month is required',
                                                    min: { value: 1, message: 'Invalid month' },
                                                    max: { value: 12, message: 'Invalid month' },
                                                })}
                                                type="number"
                                                min="1"
                                                max="12"
                                                className="input-field flex-1"
                                                placeholder="MM"
                                            />
                                            <span className="flex items-center text-gray-400">/</span>
                                            <input
                                                {...register('expiry_year', {
                                                    required: 'Expiry year is required',
                                                    min: { value: new Date().getFullYear(), message: 'Invalid year' },
                                                })}
                                                type="number"
                                                min={new Date().getFullYear()}
                                                className="input-field flex-1"
                                                placeholder="YYYY"
                                            />
                                        </div>
                                        {(errors.expiry_month || errors.expiry_year) && (
                                            <p className="mt-1 text-sm text-red-600">
                                                {errors.expiry_month?.message || errors.expiry_year?.message}
                                            </p>
                                        )}
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            CVV
                                        </label>
                                        <input
                                            {...register('cvv', {
                                                required: 'CVV is required',
                                                validate: (value) => validateCVV(value) || 'Invalid CVV',
                                            })}
                                            type="text"
                                            maxLength="4"
                                            className="input-field"
                                            placeholder="123"
                                        />
                                        {errors.cvv && (
                                            <p className="mt-1 text-sm text-red-600">{errors.cvv.message}</p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between pt-4">
                                <p className="text-sm text-gray-600">
                                    <CreditCard className="w-4 h-4 inline mr-1" />
                                    This is a mock payment system for demonstration purposes.
                                </p>
                                <button
                                    type="submit"
                                    disabled={purchaseLoading}
                                    className="button-primary"
                                >
                                    {purchaseLoading ? 'Processing...' : 'Purchase Ballots'}
                                </button>
                            </div>
                        </form>
                    </div>
                )}
            </div>

            {/* Unassigned Ballots Section */}
            <div className="card card-hover">
                <button
                    onClick={() => toggleSection('unassigned')}
                    className="card-header-button"
                >
                    <div className="flex items-center">
                        <Ticket className="w-5 h-5 text-yellow-600 mr-3" />
                        <h2 className="text-lg font-semibold text-gray-900" data-testid="unassigned-ballots-title">
                            Unassigned Ballots ({ballots?.unassigned_ballots.length || 0})
                        </h2>
                    </div>
                    {expandedSections.unassigned ? (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                    ) : (
                        <ChevronRight className="w-5 h-5 text-gray-500" />
                    )}
                </button>

                {expandedSections.unassigned && (
                    <div className="px-6 pb-6">
                        {ballots?.unassigned_ballots.length === 0 ? (
                            <p className="text-gray-600 py-4">No unassigned ballots. Purchase some to get started!</p>
                        ) : (
                            <div className="space-y-4">
                                <div className="card card-hover p-4">
                                    <div className="mb-4">
                                        <h3 className="text-sm font-medium text-yellow-800">
                                            {ballots.unassigned_ballots.length} Unassigned Ballot{ballots.unassigned_ballots.length !== 1 ? 's' : ''}
                                        </h3>
                                        <p className="text-sm text-yellow-700 mt-1">
                                            Assign your ballots to draws to participate in the lottery.
                                        </p>
                                    </div>

                                    {/* Assignment Form */}
                                    <form onSubmit={assignmentForm.handleSubmit(onSubmitAssignment)} className="space-y-4">
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    Select Draw
                                                </label>
                                                <select
                                                    {...assignmentForm.register('draw_id', {
                                                        required: 'Please select a draw',
                                                    })}
                                                    className="input-field"
                                                >
                                                    <option value="">Choose a draw...</option>
                                                    {draws.map((draw) => (
                                                        <option key={draw.id} value={draw.id}>
                                                            {draw.drawtype.name} - {formatDate(draw.date)}
                                                        </option>
                                                    ))}
                                                </select>
                                                {assignmentForm.formState.errors.draw_id && (
                                                    <p className="mt-1 text-sm text-red-600">
                                                        {assignmentForm.formState.errors.draw_id.message}
                                                    </p>
                                                )}
                                            </div>

                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    Number of Ballots
                                                </label>
                                                <input
                                                    {...assignmentForm.register('quantity', {
                                                        required: 'Quantity is required',
                                                        min: { value: 1, message: 'Minimum 1 ballot' },
                                                        max: { value: ballots?.unassigned_ballots.length || 1, message: `Maximum ${ballots?.unassigned_ballots.length || 1} ballots` },
                                                    })}
                                                    type="number"
                                                    min="1"
                                                    max={ballots?.unassigned_ballots.length || 1}
                                                    defaultValue="1"
                                                    className="input-field"
                                                />
                                                {assignmentForm.formState.errors.quantity && (
                                                    <p className="mt-1 text-sm text-red-600">
                                                        {assignmentForm.formState.errors.quantity.message}
                                                    </p>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex justify-end">
                                            <button
                                                data-testid="assign-button"
                                                type="submit"
                                                disabled={assignmentLoading}
                                                className="button-primary disabled:opacity-50"
                                            >
                                                {assignmentLoading ? 'Assigning...' : 'Assign Ballot'}
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Assigned Ballots Section (Open Draws Only) */}
            <div className="card card-hover">
                <button
                    onClick={() => toggleSection('assigned')}
                    className="card-header-button"
                >
                    <div className="flex items-center">
                        <Ticket className="w-5 h-5 text-green-600 mr-3" />
                        <h2 className="text-lg font-semibold text-gray-900" data-testid="assigned-ballots-title">
                            Assigned Ballots (Open Draws) ({ballots?.assigned_ballots.filter(ballot => ballot.draw && !ballot.draw.closed).length || 0})
                        </h2>
                    </div>
                    {expandedSections.assigned ? (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                    ) : (
                        <ChevronRight className="w-5 h-5 text-gray-500" />
                    )}
                </button>

                {expandedSections.assigned && (
                    <div className="px-6 pb-6">
                        {(() => {
                            const openDrawBallots = ballots?.assigned_ballots.filter(ballot => ballot.draw && !ballot.draw.closed) || [];
                            if (openDrawBallots.length === 0) {
                                return <p className="text-gray-600 py-4">No ballots assigned to open draws. Assign your ballots to participate!</p>;
                            }

                            // Group ballots by draw and sort by draw date (soonest first)
                            const drawGroups = openDrawBallots.reduce((groups, ballot) => {
                                const drawId = ballot.draw!.id;
                                if (!groups[drawId]) {
                                    groups[drawId] = {
                                        draw: ballot.draw!,
                                        ballots: []
                                    };
                                }
                                groups[drawId].ballots.push(ballot);
                                return groups;
                            }, {} as Record<number, { draw: any; ballots: any[] }>);

                            const sortedDraws = Object.values(drawGroups).sort((a, b) =>
                                new Date(a.draw.date).getTime() - new Date(b.draw.date).getTime()
                            );

                            return (
                                <div className="space-y-4">
                                    {sortedDraws.map((drawGroup) => (
                                        <div key={drawGroup.draw.id} className="card card-hover p-4">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="text-sm font-medium text-gray-900">
                                                    <div>{drawGroup.draw.drawtype.name} - {formatDate(drawGroup.draw.date)}</div>
                                                    <div className="text-green-600 font-medium">Participating with {drawGroup.ballots.length} ballot{drawGroup.ballots.length !== 1 ? 's' : ''}</div>
                                                </div>
                                            </div>


                                        </div>
                                    ))}
                                </div>
                            );
                        })()}
                    </div>
                )}
            </div>

            {/* Winning Ballots Section */}
            <div className="card card-hover">
                <button
                    onClick={() => toggleSection('winning')}
                    className="card-header-button"
                >
                    <div className="flex items-center">
                        <Euro className="w-5 h-5 text-yellow-600 mr-3" />
                        <h2 className="text-lg font-semibold text-gray-900" data-testid="winning-ballots-title">
                            Winning Ballots ({ballots?.assigned_ballots.filter(ballot => ballot.prize).length || 0})
                        </h2>
                    </div>
                    {expandedSections.winning ? (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                    ) : (
                        <ChevronRight className="w-5 h-5 text-gray-500" />
                    )}
                </button>

                {expandedSections.winning && (
                    <div className="px-6 pb-6">
                        {(() => {
                            const winningBallots = ballots?.assigned_ballots.filter(ballot => ballot.prize) || [];
                            if (winningBallots.length === 0) {
                                return <p className="text-gray-600 py-4">No winning ballots yet. Keep participating to win prizes!</p>;
                            }

                            // Group winning ballots by draw and sort by draw date (recent first)
                            const drawGroups = winningBallots.reduce((groups, ballot) => {
                                const drawId = ballot.draw!.id;
                                if (!groups[drawId]) {
                                    groups[drawId] = {
                                        draw: ballot.draw!,
                                        ballots: []
                                    };
                                }
                                groups[drawId].ballots.push(ballot);
                                return groups;
                            }, {} as Record<number, { draw: any; ballots: any[] }>);

                            const sortedDraws = Object.values(drawGroups).sort((a, b) =>
                                new Date(b.draw.date).getTime() - new Date(a.draw.date).getTime()
                            );

                            return (
                                <div className="space-y-4">
                                    {sortedDraws.map((drawGroup) => (
                                        <div key={drawGroup.draw.id} className="card card-hover p-4">
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-sm font-medium text-gray-900">
                                                    {drawGroup.draw.drawtype.name} - {formatDate(drawGroup.draw.date)}
                                                </span>
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                    Winner!
                                                </span>
                                            </div>

                                            <div className="space-y-1">
                                                {drawGroup.ballots.map((ballot) => (
                                                    <div key={ballot.id} className="flex items-center text-sm text-gray-600">
                                                        <span className="font-medium text-green-600">
                                                            {ballot.prize?.name} - {formatCurrency(ballot.prize?.amount || 0)}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            );
                        })()}
                    </div>
                )}
            </div>


        </div>
    );
} 
