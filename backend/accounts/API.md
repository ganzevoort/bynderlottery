# Accounts API Documentation

This document describes the REST API endpoints for the accounts app.

## Base URL
All endpoints are prefixed with `/api/accounts/`

## Authentication
- **Session Authentication**: Uses Django's session-based authentication
- **Protected Endpoints**: Require authentication and return 403 Forbidden if not authenticated

## Endpoints

### 1. User Signup
**POST** `/api/accounts/signup/`

Creates a new user account. The user will be inactive until email verification.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123",
    "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
    "message": "Account created successfully. Please check your email to verify your account.",
    "user_id": 1
}
```

**Validation Errors (400 Bad Request):**
- Passwords don't match
- Email already exists
- Invalid email format
- Password too short (minimum 8 characters)

---

### 2. User Signin
**POST** `/api/accounts/signin/`

Authenticates a user and creates a session.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Successfully signed in",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe"
    }
}
```

**Validation Errors (400 Bad Request):**
- Invalid email or password
- Account not active (email not verified)

---

### 3. User Signout
**POST** `/api/accounts/signout/`

Logs out the current user and destroys the session.

**Response (200 OK):**
```json
{
    "message": "Successfully signed out"
}
```

**Authentication Required:** Yes

---

### 4. Email Verification
**GET** `/api/accounts/verify-email/{token}/`

Verifies a user's email address using the token sent in the verification email.

**Response (200 OK):**
```json
{
    "message": "Email verified successfully. You can now sign in."
}
```

**Error (400 Bad Request):**
```json
{
    "error": "Invalid verification link."
}
```

---

### 5. Resend Verification Email
**POST** `/api/accounts/resend-verification/`

Resends the verification email to an unverified account.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "If an account with that email exists, a verification email has been sent."
}
```

**Error (400 Bad Request):**
```json
{
    "error": "Account is already verified"
}
```

---

### 6. Forgot Password
**POST** `/api/accounts/forgot-password/`

Sends a password reset email to the user.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "If an account with that email exists, a password reset email has been sent."
}
```

---

### 7. Reset Password
**POST** `/api/accounts/reset-password/{token}/`

Resets the user's password using the token from the reset email.

**Request Body:**
```json
{
    "password1": "newpassword123",
    "password2": "newpassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset successfully. You can now sign in with your new password."
}
```

**Validation Errors (400 Bad Request):**
- Passwords don't match
- Password too short (minimum 8 characters)
- Invalid or expired reset token

---

### 8. User Profile
**GET** `/api/accounts/profile/`

Retrieves the current user's profile information.

**Response (200 OK):**
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "date_joined": "2025-01-01T00:00:00Z"
    },
    "bankaccount": "NL91ABNA0417164300",
    "email_verified": true,
    "created_at": "2025-01-01T00:00:00Z"
}
```

**Authentication Required:** Yes

---

**PUT** `/api/accounts/profile/`

Updates the current user's profile information.

**Request Body:**
```json
{
    "name": "Updated Name",
    "bankaccount": "NL91ABNA0417164300"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "Updated Name",
        "date_joined": "2025-01-01T00:00:00Z"
    },
    "bankaccount": "NL91ABNA0417164300",
    "email_verified": true,
    "created_at": "2025-01-01T00:00:00Z"
}
```

**Authentication Required:** Yes

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
    "email": ["A user with this email already exists."],
    "password1": ["This password is too short. It must contain at least 8 characters."],
    "non_field_errors": ["Passwords don't match."]
}
```

## Security Features

1. **Email Verification**: Users must verify their email before they can sign in
2. **Password Requirements**: Minimum 8 characters
3. **Token Expiration**: Verification and reset tokens expire after 24 hours
4. **Security Messages**: Generic success messages don't reveal if emails exist
5. **Session Authentication**: Secure session-based authentication
6. **Input Validation**: Comprehensive validation on all inputs 
