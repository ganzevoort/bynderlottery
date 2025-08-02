# Code Walkthrough: Lottery System Development Journey

This document provides a chronological walkthrough of the Lottery System development process, from initial setup to production deployment. This represents approximately 4 days of development work and demonstrates modern full-stack development practices.

## 🚀 Phase 1: Foundation Setup

### Docker Environment & Python Backend

**Goal**: Create a simple, containerized development environment

**Implementation**:
- **Docker Compose**: Set up multi-service environment with `compose.yaml`
- **Python Backend**: Django web application with admin interface
- **Template Views**: Traditional server-side rendering for initial development

```yaml
# compose.yaml - Development environment
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  postgres:
    image: postgres:15
```

**Key Files**:
- [`compose.yaml`](../compose.yaml) - Development environment
- [`backend/`](../backend/) - Django application
- [`backend/service/settings/`](../backend/service/settings/) - Django configuration

## 🔄 Phase 2: Asynchronous Task Processing

### Problem: Email-Dependent Features

**Challenge**: Features like password reset require email sending, which can be slow.

**Solution**: Added Celery + Redis + PostgreSQL for robust async task handling

**Implementation**:

[`backend/accounts/tasks.py`](../backend/accounts/tasks.py)

```python
@celery_app.task(ignore_result=True)
def send_password_reset_email(user_email, reset_token):
    user = User.objects.get(email=email)
    ...
    send_templated_email(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=user.email,
        subject="Reset your password",
        template_name="accounts/email/password_reset",
        context_dict={"reset_url": reset_url, "user": user},
    )
```

[`backend/accounts/views.py`](../backend/accounts/views.py)

```python
from .tasks import send_password_reset_email

def forgot_password_view(request):
    """Handle password reset request."""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            send_password_reset_email.delay(email)
            messages.success(
                request,
                "If an account with that email exists, a password reset link "
                "has been sent.",
            )
            return redirect("accounts:signin")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgot_password.html", {"form": form})
```

**Key Features**:
- **Celery Workers**: Background task processing
- **Redis**: Message broker for task queue
- **PostgreSQL**: Persistent data storage
- **HTML Email Templates**: Professional-looking emails

**Key Files**:
- [`backend/accounts/tasks.py`](../backend/accounts/tasks.py) - Async tasks
- [`backend/accounts/templates/accounts/email/`](../backend/accounts/templates/accounts/email/) - Email templates
- [`backend/service/settings/defaults.py`](../backend/service/settings/defaults.py) - Celery configuration

## 🌐 Phase 3: API-First Architecture

### Django REST Framework Integration

**Goal**: Separate frontend from backend for better user experience

**Implementation**:

[`backend/accounts/api_views.py`](../backend/accounts/api_views.py)

```python
class SignupView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send verification email asynchronously
            send_verification_email.delay(user.email)
            return Response({'message': 'Account created successfully'}, status=201)
```

**Key Features**:
- **RESTful API**: Clean separation of concerns
- **Serializers**: Data validation and transformation
- **Async Email**: Non-blocking user registration
- **Session Authentication**: Traditional Django session-based auth

**Key Files**:
- [`backend/accounts/api_views.py`](../backend/accounts/api_views.py) - API endpoints
- [`backend/accounts/serializers.py`](../backend/accounts/serializers.py) - Data serialization
- [`backend/lottery/api_views.py`](../backend/lottery/api_views.py) - Lottery API
- [`backend/lottery/serializers.py`](../backend/lottery/serializers.py) - Lottery data serialization

**API Documentation**:
- [Swagger](https://bynderlottery.online/api/docs/)
- [ReDoc](https://bynderlottery.online/api/redoc/)

## ⚛️ Phase 4: Modern Frontend

### Next.js Frontend Development

**Goal**: Create responsive, modern user interface with better user journeys

**Implementation**:
```typescript
// frontend/src/lib/api.ts
export const signup = async (userData: SignupData) => {
  const response = await fetch('/api/accounts/signup/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return response.json();
};
```

**Key Features**:
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern styling
- **React Hooks**: State management
- **Responsive Design**: Mobile-first approach

**Key Files**:
- [`frontend/src/app/`](../frontend/src/app/) - Next.js app router
- [`frontend/src/components/`](../frontend/src/components/) - React components
- [`frontend/src/lib/`](../frontend/src/lib/) - API utilities

## 🧪 Phase 5: Integration Testing

### Cypress End-to-End Testing

**Goal**: Ensure reliable, automated testing of complete user journeys

**Implementation**:

[`cypress/e2e/tests/03-signup-journey.cy.ts`](../cypress/e2e/tests/03-signup-journey.cy.ts)

```typescript
describe('Signup Journey', () => {
  it('Complete signup journey: signup, verify email, signin', () => {
    // Step 1: Sign up
    cy.visit('/auth/signup')
    cy.get('input[name="name"]').type(testUser.name)
    cy.get('input[name="email"]').type(testUser.email)
    cy.get('button[type="submit"]').click()

    // Step 2: Verify email (using test API)
    cy.getTestTokens(testUser.email).then((response) => {
      const emailToken = response.body.email_verification_token
      cy.visit(`/auth/verify-email/${emailToken}`)
    })

    // Step 3: Sign in
    cy.visit('/auth/signin')
    cy.get('input[id="email"]').type(testUser.email)
    cy.get('button[type="submit"]').click()
    cy.get('div').contains('Successfully signed in!').should('be.visible')
  });
});
```

**Key Features**:
- **Test Environment**: Dedicated [`compose.test.yaml`](../compose.test.yaml) configuration
- **Test Data Management**: Automated seeding and cleanup
- **Testing Without Email**: `getTestTokens()` API for email-dependent flows
- **Visual Testing**: Screenshots and videos for debugging

**Key Files**:
- [`cypress/e2e/tests/`](../cypress/e2e/tests/) - Integration tests
- [`compose.test.yaml`](../compose.test.yaml) - Test environment
- [`scripts/run-tests.sh`](../scripts/run-tests.sh) - Test automation

## 🎬 Phase 6: Product Demo

### Automated Demo Video Creation

**Goal**: Create professional demo videos for stakeholders

**Implementation**:

[`cypress/e2e/demo/99-demo.cy.ts`](../cypress/e2e/demo/99-demo.cy.ts)

```typescript
describe('Lottery System - Complete User Journey Demo', () => {
  it('Complete user journey: signup - verify - forgotpassword - resetpassword - signin - profile - open draws - closed draws - ballot purchase - allocate', () => {
    // Complete user journey with video recording
    cy.visit('/')
    // ... full user journey
  });
});
```

**Key Features**:
- **Video Recording**: Automated demo creation
- **Complete Journey**: End-to-end user experience
- **CI/CD Integration**: Automatic demo generation
- **Artifact Upload**: Videos available for review

## 🌍 Phase 7: Production Deployment

### Domain & Kubernetes Setup

**Goal**: Deploy to production with proper infrastructure

**Implementation**:
```yaml
# k8s/deployments.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lottery-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: lottery-backend
  template:
    spec:
      containers:
      - name: backend
        image: ghcr.io/ganzevoort/bynderlottery/backend:latest
        ports:
        - containerPort: 8000
```

**Key Features**:
- **Domain Registration**: `bynderlottery.online`
- **Kubernetes Cluster**: Scalable container orchestration
- **Load Balancing**: NGINX ingress controller
- **SSL/TLS**: Automatic certificate management
- **Monitoring**: Health checks and logging

**Key Files**:
- [`k8s/`](../k8s/) - Kubernetes manifests
- [`helm-chart/`](../helm-chart/) - Helm deployment

## 🔄 Phase 8: CI/CD Automation

### GitHub Actions Pipeline

**Goal**: Automated build, test, and deployment

**Implementation**:
```yaml
# .github/workflows/ci-cd.yml
jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ env.BACKEND_IMAGE }}:build-${{ env.COMMIT_SHA }}
          target: production

  test-integration:
    needs: [build-backend, build-frontend]
    runs-on: ubuntu-latest
    steps:
      - name: Run integration tests
        run: docker compose -f compose.test.yaml exec cypress cypress run
```

**Key Features**:
- **Multi-Stage Builds**: Optimized production images
- **Parallel Testing**: Frontend, backend, and integration tests
- **Registry Integration**: GitHub Container Registry
- **Automated Deployment**: Production deployment on main branch
- **Demo Generation**: Automatic video creation

**Key Files**:
- [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml) - CI/CD pipeline
- [`scripts/update-compose.py`](../scripts/update-compose.py) - Test environment setup
- [`Dockerfile`](../backend/Dockerfile) - Multi-stage builds

## 📊 Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   Testing       │
│   (User)        │    │   (Cypress)     │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          │                      │
          └───────┬──────────────┘
                  ▼
         ┌─────────────────┐
         │   Web/NGINX     │
         │ (Reverse Proxy) │
         └─────────┬───────┘
                   │
                   ├─────────────────┐
                   ▼                 ▼
      ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
      │   Frontend      │    │   Backend       │    │   Workers       │
      │   (Next.js)     │    │   (Django)      │    │   (Celery)      │
      └─────────────────┘    └──┬──────────────┘    └───┬──────────┬──┘
                                │                       │          │
                                ├───────────────────────┐          │
                                ▼                       ▼          ▼
                    ┌─────────────────┐  ┌─────────────────┐      ┌─────────────────┐
                    │   Database      │  │   Message Queue │      │   Email Service │
                    │   (PostgreSQL)  │  │   (Redis)       │      │   (External)    │
                    └─────────────────┘  └─────────────────┘      └─────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js + TypeScript | Modern React framework |
| **Backend** | Django + DRF | Python web framework |
| **Database** | PostgreSQL | Relational database |
| **Cache/Queue** | Redis | Message broker & caching |
| **Tasks** | Celery | Asynchronous processing |
| **Testing** | Cypress | End-to-end testing |
| **Deployment** | Kubernetes | Container orchestration |
| **CI/CD** | GitHub Actions | Automated pipeline |
| **Registry** | GitHub Container Registry | Image storage |

## 🎯 Key Achievements

### Development Efficiency
- **Containerized Development**: Consistent environment across team
- **API-First Design**: Clean separation of frontend/backend
- **Automated Testing**: Reliable test coverage
- **Modern Tooling**: TypeScript, Tailwind, Next.js

### Production Readiness
- **Scalable Architecture**: Kubernetes deployment
- **Automated Pipeline**: CI/CD from code to production
- **Monitoring**: Health checks and logging
- **Security**: SSL/TLS, proper authentication

### User Experience
- **Responsive Design**: Mobile-first approach
- **Professional Emails**: HTML templated communications
- **Smooth Journeys**: Optimized user flows
- **Demo Videos**: Stakeholder communication

## 🚀 Next Steps

### Potential Enhancements
1. **Performance**: CDN integration, caching strategies
2. **Monitoring**: Prometheus/Grafana dashboards
3. **Security**: Rate limiting, input validation
4. **Scalability**: Horizontal pod autoscaling
5. **Testing**: Visual regression testing, load testing

This walkthrough demonstrates a complete full-stack development journey from initial setup to production deployment, showcasing modern development practices and tools.
