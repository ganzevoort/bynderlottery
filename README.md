# Lottery System

A Django-based lottery platform with user authentication, ballot management, and REST API endpoints. The system supports multiple draw types, prize management, and secure user operations.

## 🏗️ Architecture Overview

The system is built with Django and consists of two main apps:

- **`accounts`**: User authentication, registration, email verification, and profile management
- **`lottery`**: Core lottery functionality including draws, ballots, prizes, and winner management

## 🚀 Features

### User Management
- ✅ **Email-based authentication** (no usernames required)
- ✅ **Account registration** with email verification
- ✅ **Password reset** functionality
- ✅ **Profile management** with bank account details
- ✅ **Session-based authentication**

### Lottery System
- ✅ **Multiple draw types** (daily, weekly, special events)
- ✅ **Prize management** with configurable amounts
- ✅ **Ballot purchasing** (mock payment processing)
- ✅ **Ballot assignment** to specific draws
- ✅ **Winner selection** and prize distribution
- ✅ **Draw scheduling** with automatic type detection

### API Endpoints
- ✅ **RESTful API** for all functionality
- ✅ **Public endpoints** for draw information
- ✅ **Protected endpoints** for user operations
- ✅ **Comprehensive validation** and error handling
- ✅ **Privacy protection** (only winner names shown)

## 📁 Project Structure

```
lottery/
├── backend/
│   ├── accounts/                 # User authentication app
│   │   ├── models.py            # Account model with User relationship
│   │   ├── forms.py             # Authentication forms
│   │   ├── views.py             # Traditional Django views
│   │   ├── serializers.py       # DRF serializers for API
│   │   ├── api_views.py         # API views
│   │   ├── tasks.py             # Celery tasks for email sending
│   │   ├── templates/           # HTML templates
│   │   └── tests.py             # Test suite
│   │
│   ├── lottery/                 # Core lottery app
│   │   ├── models.py            # Draw, Prize, Ballot models
│   │   ├── views.py             # Traditional Django views
│   │   ├── serializers.py       # DRF serializers for API
│   │   ├── api_views.py         # API views
│   │   ├── forms.py             # Ballot purchase forms
│   │   ├── templates/           # HTML templates
│   │   └── tests.py             # Test suite
│   │
│   ├── service/                 # Main project settings
│   │   ├── settings/            # Django settings
│   │   ├── templates/           # Base templates
│   │   └── static/              # Static files (logos, etc.)
│   │
│   ├── requirements.txt         # Python dependencies
│   ├── manage.py               # Django management
│   └── Dockerfile              # Container configuration
│
├── compose.yaml                 # Docker Compose configuration
└── README.md                   # This file
```

## 🗄️ Database Models

### Accounts App

#### Account Model
```python
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bankaccount = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    password_reset_token = models.CharField(max_length=100, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
```

### Lottery App

#### DrawType Model
```python
class DrawType(OrderedModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    schedule = models.JSONField(default=dict)  # {"weekday": 6} or {"month": 12, "day": 31}
```

#### Prize Model
```python
class Prize(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField()
    number = models.IntegerField(default=1)
    drawtype = models.ForeignKey(DrawType, on_delete=models.CASCADE, related_name="prizes")
```

#### Draw Model
```python
class Draw(models.Model):
    drawtype = models.ForeignKey(DrawType, on_delete=models.PROTECT, related_name="draws")
    date = models.DateField(unique=True)
    closed = models.DateTimeField(null=True, blank=True)
```

#### Ballot Model
```python
class Ballot(models.Model):
    draw = models.ForeignKey(Draw, null=True, blank=True, on_delete=models.PROTECT, related_name="ballots")
    account = models.ForeignKey(Account, null=False, on_delete=models.PROTECT, related_name="ballots")
    prize = models.ForeignKey(Prize, null=True, blank=True, on_delete=models.PROTECT, related_name="ballots")
```

## 🔌 API Endpoints

### Accounts API (`/api/accounts/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup/` | User registration | No |
| POST | `/signin/` | User authentication | No |
| POST | `/signout/` | User logout | Yes |
| GET | `/verify-email/{token}/` | Email verification | No |
| POST | `/resend-verification/` | Resend verification email | No |
| POST | `/forgot-password/` | Request password reset | No |
| POST | `/reset-password/{token}/` | Reset password | No |
| GET/PUT | `/profile/` | User profile management | Yes |

### Lottery API (`/api/lottery/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/draws/open/` | List open draws | No |
| GET | `/draws/closed/` | List closed draws with winners | No |
| GET | `/draws/{id}/` | Draw details | No |
| GET | `/stats/` | Lottery statistics | No |
| GET | `/my-ballots/` | User's ballot summary | Yes |
| GET | `/my-winnings/` | User's winnings summary | Yes |
| POST | `/purchase-ballots/` | Buy new ballots | Yes |
| POST | `/ballots/{id}/assign/` | Assign ballot to draw | Yes |
| GET | `/ballots/{id}/` | Ballot details | Yes |

## 🛠️ Setup and Installation

### Prerequisites
- Docker and Docker Compose

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lottery
   ```

2. **Build the containers**
    ```
    docker compose build
    ```

3. **Start the services**
   ```bash
   docker compose up -d
   ```
   When started, the backend container checks to see if the database is empty
   and automatically restores a dump if it is.

4. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Interface: http://localhost:8000/admin
   - API Documentation: See `backend/accounts/API.md` and `backend/lottery/API.md`

5. **Create test data**
    A superuser will be automatically created (see environment).
    Sample lottery data is available in a fixtures file:
   ```bash
   docker compose exec backend python manage.py loaddata initial
   ```

## 🔧 Configuration
Settings that may need to be different per DTAP layer are set via environment variables:

### Environment Variables
A sample `.env` file that can be used:
```bash
COMPOSE_BAKE=true
UID=501
GID=20
LAYER=dev
SECRET_KEY=ezwcjewecbserekabkgelbolfsmsekohhwgmxuvhywzmwcyzwufbukxlgdluaehg

TIME_ZONE=Europe/Amsterdam
ADMIN_PASSWORD=pmbvbfkmujghxdvn
ADMIN_EMAIL=admin@lottery.com

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@lottery.com

DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_HOST=postgres
DATABASE_NAME=myproject
DATABASE_USER=janedoe
DATABASE_PASSWORD=hcefluteyfzgwxeg

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## 🧪 Testing

### Run All Tests
```bash
docker compose exec backend python manage.py test
```

### Run Specific Test Suites
```bash
# Accounts tests
docker compose exec backend python manage.py test accounts.tests accounts.test_api

# Lottery tests
docker compose exec backend python manage.py test lottery.tests lottery.test_api
```

### Test Coverage
The test suite includes:
- ✅ **Model tests** - Database operations and relationships
- ✅ **Form tests** - Validation and data processing
- ✅ **View tests** - Traditional Django views
- ✅ **API tests** - REST API endpoints
- ✅ **Integration tests** - End-to-end workflows
- ✅ **Security tests** - Privacy and access control

## 🔒 Security Features

### Authentication & Authorization
- **Email-based login** - No usernames required
- **Email verification** - Required before account activation
- **Session authentication** - Secure session management
- **Password requirements** - Minimum 8 characters
- **Token expiration** - 24-hour expiration for security tokens

### Data Privacy
- **User isolation** - Users can only access their own data
- **Winner privacy** - Only names shown, no emails or IDs
- **Secure messages** - Generic success messages don't reveal user existence
- **Input validation** - Comprehensive validation on all inputs

### API Security
- **Authentication required** - Protected endpoints require login
- **Ownership validation** - Users can only modify their own resources
- **Draw validation** - Cannot assign ballots to closed draws
- **Rate limiting ready** - Infrastructure for implementing rate limits

## 📧 Email System

### Email Templates
- **HTML and Text versions** - Compatible with all email clients
- **Base template** - Consistent branding across all emails
- **Customizable themes** - Different colors for different email types

### Email Types
1. **Account Verification** - Welcome email with verification link
2. **Password Reset** - Secure password reset with expiration
3. **Winner Notification** - Prize notification with multiple prize support

### Celery Integration
- **Asynchronous processing** - Email sending doesn't block requests
- **Error handling** - Failed emails are logged but don't break the app
- **Mock support** - Tests use mocked email sending

## 🎨 User Interface

### Design Features
- **Bootstrap 5** - Modern, responsive design
- **Custom logo** - Euro symbol on green circle
- **Collapsible sections** - Better organization of ballot information
- **Font Awesome icons** - Professional iconography
- **Currency formatting** - Proper euro formatting with humanize

### Key Pages
1. **Home** - Overview and navigation
2. **Open Draws** - Available draws for ballot assignment
3. **Closed Draws** - Past draws with winner information
4. **My Ballots** - User's ballot management
5. **Profile** - Account settings and information

### Settings Structure
- **`service/settings/defaults.py`** - Django default settings
- **`service/settings/__init__.py`** - Custom project settings
- **`service/settings/environment.py`** - Environment-specific settings

## 🚀 Deployment

### Production Considerations
1. **Database** - Use PostgreSQL or MySQL
2. **Email** - Configure SMTP or email service (SendGrid, Mailgun)
3. **Static Files** - Use CDN or static file server
4. **Celery** - Set up Redis for task queue
5. **HTTPS** - Enable SSL/TLS encryption
6. **Monitoring** - Add logging and monitoring
7. **Backup** - Regular database backups

### Docker Production
```bash
# Build production image
docker build -t lottery:production .

# Run with production settings
docker run -e DJANGO_SETTINGS_MODULE=service.settings.production lottery:production
```

## 📚 API Documentation

### Quick API Examples

#### User Registration
```bash
curl -X POST http://localhost:8000/api/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password1": "securepass123",
    "password2": "securepass123",
    "name": "John Doe"
  }'
```

#### Purchase Ballots
```bash
curl -X POST http://localhost:8000/api/lottery/purchase-ballots/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your-session-id" \
  -d '{
    "quantity": 5,
    "card_number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123"
  }'
```

#### Get User Ballots
```bash
curl -X GET http://localhost:8000/api/lottery/my-ballots/ \
  -H "Cookie: sessionid=your-session-id"
```

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**
6. **Submit a pull request**

### Code Standards
- **PEP 8** - Python code style
- **Django best practices** - Follow Django conventions
- **Type hints** - Use type annotations where helpful
- **Docstrings** - Document functions and classes
- **Test coverage** - Maintain high test coverage

## 🆘 Support

### Common Issues

#### Email Not Sending
- Check email backend configuration
- Verify Celery is running (for async emails)
- Check logs for error messages

#### API Authentication Issues
- Ensure session cookies are included in requests
- Verify user is logged in for protected endpoints
- Check CSRF token for POST requests

#### Database Issues
- Run migrations: `python manage.py migrate`
- Check database connection settings
- Verify model relationships

### Getting Help
- **Documentation** - Check the API documentation files
- **Tests** - Review test cases for usage examples
- **Issues** - Create an issue with detailed information
- **Discussions** - Use GitHub discussions for questions

## 🔮 Future Enhancements

### Planned Features
- **Real-time notifications** - WebSocket support for live updates
- **Mobile app** - React Native or Flutter mobile application
- **Advanced analytics** - Detailed lottery statistics and trends
- **Payment integration** - Real payment processor integration
- **Multi-language support** - Internationalization
- **API rate limiting** - Protect against abuse
- **Webhook support** - External system integrations

### Technical Improvements
- **Caching** - Redis caching for improved performance
- **Monitoring** - Application performance monitoring
- **CI/CD** - Automated testing and deployment
- **Container orchestration** - Kubernetes deployment 
