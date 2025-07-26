# Lottery API Documentation

This document describes the REST API endpoints for the lottery app.

## Base URL
All endpoints are prefixed with `/api/lottery/`

## Authentication
- **Session Authentication**: Uses Django's session-based authentication
- **Public Endpoints**: Some endpoints are accessible without authentication
- **Protected Endpoints**: Require authentication and return 403 Forbidden if not authenticated

## Endpoints

### Public Endpoints (No Authentication Required)

#### 1. List Open Draws
**GET** `/api/lottery/draws/open/`

Returns a list of all open (future) draws that users can assign ballots to.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "drawtype": {
            "id": 1,
            "name": "Daily Lottery",
            "is_active": true,
            "schedule": {}
        },
        "date": "2025-01-15",
        "closed": null,
        "ballots": 0,
        "prizes": [
            {
                "id": 1,
                "name": "First Prize",
                "amount": 1000,
                "number": 1,
                "drawtype": 1
            }
        ],
        "winner_count": 0,
        "total_prize_amount": 0
    }
]
```

---

#### 2. List Closed Draws
**GET** `/api/lottery/draws/closed/`

Returns a list of all closed draws with winner information.

**Response (200 OK):**
```json
[
    {
        "id": 2,
        "drawtype": {
            "id": 1,
            "name": "Daily Lottery",
            "is_active": true,
            "schedule": {}
        },
        "date": "2025-01-08",
        "closed": "2025-01-08T20:00:00Z",
        "ballots": 5,
        "prizes": [
            {
                "id": 1,
                "name": "First Prize",
                "amount": 1000,
                "number": 1,
                "drawtype": 1
            }
        ],
        "winner_count": 1,
        "total_prize_amount": 1000,
        "winners": [
            {
                "name": "John Doe",
                "prize_name": "First Prize",
                "prize_amount": 1000
            }
        ]
    }
]
```

---

#### 3. Draw Details
**GET** `/api/lottery/draws/{id}/`

Returns detailed information about a specific draw.

**Response (200 OK):**
```json
{
    "id": 2,
    "drawtype": {
        "id": 1,
        "name": "Daily Lottery",
        "is_active": true,
        "schedule": {}
    },
    "date": "2025-01-08",
    "closed": "2025-01-08T20:00:00Z",
    "ballots": 5,
    "prizes": [
        {
            "id": 1,
            "name": "First Prize",
            "amount": 1000,
            "number": 1,
            "drawtype": 1
        }
    ],
    "winner_count": 1,
    "total_prize_amount": 1000,
    "winners": [
        {
            "name": "John Doe",
            "prize_name": "First Prize",
            "prize_amount": 1000
        }
    ]
}
```

---

#### 4. Lottery Statistics
**GET** `/api/lottery/stats/`

Returns public statistics about the lottery system.

**Response (200 OK):**
```json
{
    "total_draws": 10,
    "open_draws": 3,
    "closed_draws": 7,
    "total_prizes_awarded": 15,
    "total_amount_awarded": 15000,
    "recent_winners": [
        {
            "draw": {
                "id": 2,
                "drawtype_name": "Daily Lottery",
                "date": "2025-01-08"
            },
            "winners": [
                {
                    "name": "John Doe",
                    "prize_name": "First Prize",
                    "prize_amount": 1000
                }
            ]
        }
    ]
}
```

---

### Protected Endpoints (Authentication Required)

#### 5. User Ballots
**GET** `/api/lottery/my-ballots/`

Returns the current user's ballot summary, including unassigned and assigned ballots.

**Response (200 OK):**
```json
{
    "unassigned_ballots": [
        {
            "id": 1,
            "draw": null,
            "prize": null
        }
    ],
    "assigned_ballots": [
        {
            "draw": {
                "id": 1,
                "drawtype": {
                    "id": 1,
                    "name": "Daily Lottery",
                    "is_active": true,
                    "schedule": {}
                },
                "date": "2025-01-15",
                "closed": null,
                "ballots": 1,
                "prizes": [...],
                "winner_count": 0,
                "total_prize_amount": 0
            },
            "ballots": [
                {
                    "id": 2,
                    "draw": 1,
                    "prize": null
                }
            ]
        }
    ],
    "total_ballots": 2
}
```

**Authentication Required:** Yes

---

#### 6. User Winnings
**GET** `/api/lottery/my-winnings/`

Returns the current user's winnings summary.

**Response (200 OK):**
```json
{
    "total_winnings": 2500,
    "total_winning_ballots": 2,
    "winnings_by_draw": [
        {
            "draw": {
                "id": 2,
                "drawtype_name": "Daily Lottery",
                "date": "2025-01-08"
            },
            "prizes": [
                {
                    "prize_name": "First Prize",
                    "prize_amount": 1000
                },
                {
                    "prize_name": "Second Prize",
                    "prize_amount": 500
                }
            ]
        }
    ]
}
```

**Authentication Required:** Yes

---

#### 7. Purchase Ballots
**POST** `/api/lottery/purchase-ballots/`

Purchases new ballots for the current user (mock implementation).

**Request Body:**
```json
{
    "quantity": 5,
    "card_number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123"
}
```

**Response (201 Created):**
```json
{
    "message": "Successfully purchased 5 ballot(s)",
    "ballots_created": 5,
    "total_ballots": 7
}
```

**Validation Errors (400 Bad Request):**
- Invalid quantity (must be 1-100)
- Invalid card number format
- Invalid expiry month (1-12)
- Invalid expiry year (2025-2030)
- Invalid CVV (3-4 digits)

**Authentication Required:** Yes

---

#### 8. Assign Ballot to Draw
**POST** `/api/lottery/ballots/{ballot_id}/assign/`

Assigns an unassigned ballot to a specific draw.

**Request Body:**
```json
{
    "draw_id": 1
}
```

**Response (200 OK):**
```json
{
    "message": "Ballot successfully assigned to Daily Lottery draw on 2025-01-15",
    "ballot_id": 1,
    "draw_id": 1
}
```

**Validation Errors (400 Bad Request):**
- Ballot already assigned to a draw
- Draw does not exist
- Draw is closed

**Authentication Required:** Yes

---

#### 9. Ballot Details
**GET** `/api/lottery/ballots/{id}/`

Returns details of a specific ballot belonging to the current user.

**Response (200 OK):**
```json
{
    "id": 1,
    "draw": {
        "id": 1,
        "drawtype": {
            "id": 1,
            "name": "Daily Lottery",
            "is_active": true,
            "schedule": {}
        },
        "date": "2025-01-15",
        "closed": null,
        "ballots": 1,
        "prizes": [...],
        "winner_count": 0,
        "total_prize_amount": 0
    },
    "prize": null
}
```

**Authentication Required:** Yes

---

## Error Responses

All endpoints return appropriate HTTP status codes:

- **200 OK**: Success
- **201 Created**: Resource created successfully
- **400 Bad Request**: Validation errors or invalid data
- **401 Unauthorized**: Authentication required (not used in this API)
- **403 Forbidden**: Permission denied (authentication required)
- **404 Not Found**: Resource not found

Error responses include details about what went wrong:

```json
{
    "quantity": ["Ensure this value is greater than or equal to 1."],
    "card_number": ["Card number must contain only digits"],
    "draw_id": ["Cannot assign ballot to a closed draw"]
}
```

## Security Features

1. **User Isolation**: Users can only access their own ballots and winnings
2. **Privacy Protection**: Winner information only shows names, not emails or other sensitive data
3. **Draw Validation**: Cannot assign ballots to closed draws
4. **Ballot Ownership**: Users can only assign their own ballots
5. **Input Validation**: Comprehensive validation on all inputs
6. **Session Authentication**: Secure session-based authentication

## Data Privacy

- **Winner Information**: Only displays winner names and prize amounts
- **User Data**: No email addresses, user IDs, or other sensitive information is exposed
- **Ballot Privacy**: Users can only see their own ballots
- **Draw Information**: Public draw information is available to all users

## Mock Payment Processing

The ballot purchase endpoint includes mock payment processing for demonstration purposes. In a production environment, this would integrate with a real payment processor (Stripe, PayPal, etc.).

## Rate Limiting

Consider implementing rate limiting for:
- Ballot purchases
- Ballot assignments
- API requests in general

## Future Enhancements

Potential API enhancements:
- Pagination for large result sets
- Filtering and sorting options
- Real-time notifications for draw results
- Webhook support for external integrations
- Advanced search functionality
- Bulk operations for ballot management 
