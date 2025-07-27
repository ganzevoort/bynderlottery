// User and Account types
export interface User {
    id: number;
    email: string;
    name: string;
    is_active: boolean;
}

export interface Account {
    id: number;
    user: User;
    bankaccount: string;
    email_verified: boolean;
}

// Lottery types
export interface DrawType {
    id: number;
    name: string;
    is_active: boolean;
    schedule: Record<string, any>;
}

export interface Prize {
    id: number;
    name: string;
    amount: number;
    number: number;
    drawtype: number;
}

export interface Draw {
    id: number;
    drawtype: DrawType;
    date: string;
    closed: string | null;
    prizes: Prize[];
    winner_count: number;
    total_prize_amount: number;
    winners?: Winner[];
}

export interface Winner {
    name: string;
    prize_name: string;
    prize_amount: number;
}

export interface Ballot {
    id: number;
    draw: Draw | null;
    prize: Prize | null;
}

export interface UserBallots {
    unassigned_ballots: Ballot[];
    assigned_ballots: Ballot[];
    total_ballots: number;
}

export interface UserWinnings {
    total_winnings: number;
    total_ballots_won: number;
    recent_wins: Array<{
        draw_date: string;
        draw_name: string;
        prize_name: string;
        prize_amount: number;
    }>;
}

export interface LotteryStats {
    total_draws: number;
    total_prizes_awarded: number;
    total_amount_awarded: number;
    active_draws: number;
}

// Form types
export interface SignUpForm {
    email: string;
    password1: string;
    password2: string;
    name: string;
}

export interface SignInForm {
    email: string;
    password: string;
}

export interface ForgotPasswordForm {
    email: string;
}

export interface ResetPasswordForm {
    password1: string;
    password2: string;
}

export interface ProfileForm {
    name: string;
    bankaccount: string;
}

export interface BallotPurchaseForm {
    quantity: number;
    card_number: string;
    expiry_month: number;
    expiry_year: number;
    cvv: string;
}

export interface BallotAssignmentForm {
    draw_id: number;
    quantity: number;
}

// API Response types
export interface ApiResponse<T> {
    data: T;
    message?: string;
}

export interface ErrorResponse {
    message: string;
    errors?: Record<string, string[]>;
} 
