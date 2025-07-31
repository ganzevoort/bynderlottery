import api from './api';
import {
  Draw,
  UserBallots,
  UserWinnings,
  LotteryStats,
  BallotPurchaseForm,
  BallotAssignmentForm,
} from './types';

export class LotteryService {
  static async getOpenDraws(): Promise<Draw[]> {
    const response = await api.get('/lottery/draws/open/');
    return response.data;
  }

  static async getClosedDraws(): Promise<Draw[]> {
    const response = await api.get('/lottery/draws/closed/');
    return response.data;
  }

  static async getDrawDetail(id: number): Promise<Draw> {
    const response = await api.get(`/lottery/draws/${id}/`);
    return response.data;
  }

  static async getLotteryStats(): Promise<LotteryStats> {
    const response = await api.get('/lottery/stats/');
    return response.data;
  }

  static async getUserBallots(): Promise<UserBallots> {
    const response = await api.get('/lottery/my-ballots/');
    return response.data;
  }

  static async getUserWinnings(): Promise<UserWinnings> {
    const response = await api.get('/lottery/my-winnings/');
    return response.data;
  }

  static async purchaseBallots(
    data: BallotPurchaseForm
  ): Promise<{ message: string; ballots_created: number }> {
    const response = await api.post('/lottery/purchase-ballots/', data);
    return response.data;
  }

  static async assignBallot(
    ballotId: number,
    data: BallotAssignmentForm
  ): Promise<{ message: string }> {
    const response = await api.post(
      `/lottery/ballots/${ballotId}/assign/`,
      data
    );
    return response.data;
  }

  static async getBallotDetail(
    id: number
  ): Promise<{ id: number; draw: Draw | null; prize: unknown | null }> {
    const response = await api.get(`/lottery/ballots/${id}/`);
    return response.data;
  }
}
