#!/bin/bash

# Lottery System Cypress Test Runner
# This script provides easy commands to run different types of tests using a separate test environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test-specific compose file
COMPOSE_FILE="compose.test.yaml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if test containers are running
check_test_containers() {
    if ! docker compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        print_warning "Test containers are not running. Starting them..."
        docker compose -f $COMPOSE_FILE up -d
        sleep 15  # Wait for containers to be ready
    fi
}

# Function to run tests
run_tests() {
    local test_spec="$1"
    local test_name="$2"
    
    print_status "Running $test_name..."
    
            if docker compose -f $COMPOSE_FILE exec cypress cypress run --spec "$test_spec"; then
        print_success "$test_name completed successfully!"
    else
        print_error "$test_name failed!"
        exit 1
    fi
}

# Function to setup test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Stop any existing test containers
    docker compose -f $COMPOSE_FILE down --volumes --remove-orphans
    
    # Start test containers
    docker compose -f $COMPOSE_FILE up -d
    
    print_status "Waiting for services to be ready..."
    sleep 20
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    for i in {1..30}; do
        if docker compose -f $COMPOSE_FILE exec -T backend python -c "import django; print('Django ready')" 2>/dev/null; then
            print_success "Backend is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 60 seconds"
            docker compose -f $COMPOSE_FILE logs backend
            exit 1
        fi
        sleep 2
    done
    
    # Run migrations and seed test data
    print_status "Setting up database..."
    if ! docker compose -f $COMPOSE_FILE exec -T backend python manage.py migrate; then
        print_error "Failed to run migrations"
        docker compose -f $COMPOSE_FILE logs backend
        exit 1
    fi
    
    if ! docker compose -f $COMPOSE_FILE exec -T backend python manage.py seed_test_data; then
        print_error "Failed to seed test data"
        docker compose -f $COMPOSE_FILE logs backend
        exit 1
    fi
    
    print_success "Test environment setup complete!"
    print_status "Test application available at: http://localhost:8081"
}

# Main script logic
case "${1:-help}" in
    "all")
        check_docker
        setup_test_env
        print_status "Running all Cypress tests..."
        docker compose -f $COMPOSE_FILE exec cypress cypress run
        print_success "All tests completed!"
        ;;
    
    "demo")
        check_docker
        setup_test_env
        run_tests "e2e/99-demo.cy.ts" "Complete Demo Journey"
        ;;
    
    "api")
        check_docker
        setup_test_env
        run_tests "e2e/01-api-tests.cy.ts" "API Tests"
        ;;
    
    "signup-journey")
        check_docker
        setup_test_env
        run_tests "e2e/03-signup-journey.cy.ts" "Signup Journey Tests"
        ;;
    
    "password-reset-journey")
        check_docker
        setup_test_env
        run_tests "e2e/04-password-reset-journey.cy.ts" "Password Reset Journey Tests"
        ;;
    
    "profile-journey")
        check_docker
        setup_test_env
        run_tests "e2e/05-profile-journey.cy.ts" "Profile Journey Tests"
        ;;
    
    "ballot-journey")
        check_docker
        setup_test_env
        run_tests "e2e/06-ballot-journey.cy.ts" "Ballot Journey Tests"
        ;;
    
    "closed-draws-journey")
        check_docker
        setup_test_env
        run_tests "e2e/07-closed-draws-journey.cy.ts" "Closed Draws Journey Tests"
        ;;
    
    "token-tests")
        check_docker
        setup_test_env
        run_tests "e2e/02-token-tests.cy.ts" "Token Tests"
        ;;
    
    "interactive")
        check_docker
        setup_test_env
        print_status "Opening Cypress in interactive mode..."
        docker compose -f $COMPOSE_FILE exec -it cypress cypress open
        ;;
    
    "setup")
        check_docker
        setup_test_env
        ;;
    
    "clean")
        print_status "Cleaning up test environment..."
        docker compose -f $COMPOSE_FILE down --volumes --remove-orphans
        print_success "Cleanup complete!"
        ;;
    
    "logs")
        print_status "Showing test environment logs..."
        docker compose -f $COMPOSE_FILE logs -f
        ;;
    
    "status")
        print_status "Test environment status:"
        docker compose -f $COMPOSE_FILE ps
        ;;
    
    "restart")
        print_status "Restarting test environment..."
        docker compose -f $COMPOSE_FILE restart
        print_success "Test environment restarted!"
        ;;
    
    "shell")
        check_docker
        setup_test_env
        print_status "Opening backend shell..."
        docker compose -f $COMPOSE_FILE exec backend python manage.py shell
        ;;
    
    "migrate")
        check_docker
        setup_test_env
        print_status "Running migrations..."
        docker compose -f $COMPOSE_FILE exec backend python manage.py migrate
        print_success "Migrations completed!"
        ;;
    
    "seed")
        check_docker
        setup_test_env
        print_status "Seeding test data..."
        docker compose -f $COMPOSE_FILE exec backend python manage.py seed_test_data
        print_success "Test data seeded!"
        ;;
    
    "backend-tests")
        check_docker
        setup_test_env
        print_status "Running Django unit tests..."
        if docker compose -f $COMPOSE_FILE exec -T backend python manage.py test; then
            print_success "Django unit tests completed successfully!"
        else
            print_error "Django unit tests failed!"
            exit 1
        fi
        ;;
    
    "backend-lint")
        check_docker
        setup_test_env
        print_status "Running flake8 linting..."
        if docker compose -f $COMPOSE_FILE exec -T backend flake8 .; then
            print_success "Linting completed successfully!"
        else
            print_error "Linting failed!"
            exit 1
        fi
        ;;
    
    "backend-format")
        check_docker
        setup_test_env
        print_status "Running black formatting check..."
        if docker compose -f $COMPOSE_FILE exec -T backend black --check .; then
            print_success "Code formatting check completed successfully!"
        else
            print_error "Code formatting check failed!"
            exit 1
        fi
        ;;
    
    "backend-check")
        check_docker
        setup_test_env
        print_status "Running all backend checks..."
        
        # Run linting
        print_status "Running flake8 linting..."
        if ! docker compose -f $COMPOSE_FILE exec -T backend flake8 .; then
            print_error "Linting failed!"
            exit 1
        fi
        
        # Run formatting check
        print_status "Running black formatting check..."
        if ! docker compose -f $COMPOSE_FILE exec -T backend black --check .; then
            print_error "Code formatting check failed!"
            exit 1
        fi
        
        # Run unit tests
        print_status "Running Django unit tests..."
        if ! docker compose -f $COMPOSE_FILE exec -T backend python manage.py test; then
            print_error "Django unit tests failed!"
            exit 1
        fi
        
        print_success "All backend checks completed successfully!"
        ;;
    
    "full-test")
        check_docker
        setup_test_env
        print_status "Running full test suite (backend + frontend)..."
        
        # Run backend checks
        print_status "Running backend checks..."
        if ! docker compose -f $COMPOSE_FILE exec -T backend flake8 .; then
            print_error "Backend linting failed!"
            exit 1
        fi
        
        if ! docker compose -f $COMPOSE_FILE exec -T backend black --check .; then
            print_error "Backend formatting check failed!"
            exit 1
        fi
        
        if ! docker compose -f $COMPOSE_FILE exec -T backend python manage.py test; then
            print_error "Backend unit tests failed!"
            exit 1
        fi
        
        print_success "Backend checks completed successfully!"
        
        # Run frontend tests
        print_status "Running frontend tests..."
        if docker compose -f $COMPOSE_FILE exec cypress cypress run; then
            print_success "Frontend tests completed successfully!"
        else
            print_error "Frontend tests failed!"
            exit 1
        fi
        
        print_success "Full test suite completed successfully!"
        ;;
    
    "help"|*)
        echo "Lottery System Test Runner"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Frontend Tests (Cypress):"
        echo "  all                    Run all Cypress tests"
        echo "  api                    Run API tests only"
        echo "  token-tests            Run token tests only"
        echo "  signup-journey         Run signup journey tests only"
        echo "  password-reset-journey Run password reset journey tests only"
        echo "  profile-journey        Run profile journey tests only"
        echo "  ballot-journey         Run ballot journey tests only"
        echo "  closed-draws-journey   Run closed draws journey tests only"
        echo "  demo                   Run complete demo journey for product owner"
        echo "  interactive            Open Cypress in interactive mode"
        echo ""
        echo "Backend Tests:"
        echo "  backend-tests          Run Django unit tests"
        echo "  backend-lint           Run flake8 linting"
        echo "  backend-format         Run black formatting check"
        echo "  backend-check          Run all backend checks (lint + format + tests)"
        echo ""
        echo "Full Test Suite:"
        echo "  full-test              Run all tests (backend + frontend)"
        echo ""
        echo "Environment Management:"
        echo "  setup                  Set up test environment (start containers + migrate + seed data)"
        echo "  clean                  Stop all test containers and remove volumes"
        echo "  logs                   Show test environment logs"
        echo "  status                 Show test environment status"
        echo "  restart                Restart test environment"
        echo "  shell                  Open Django shell in test environment"
        echo "  migrate                Run database migrations"
        echo "  seed                   Seed test data"
        echo "  help                   Show this help message"
        echo ""
        echo "Cypress Test Structure:"
        echo "  01-api-tests.cy.ts              - API endpoint validation"
        echo "  02-token-tests.cy.ts            - Email verification and password reset tokens"
        echo "  03-signup-journey.cy.ts         - Complete signup and email verification flow"
        echo "  04-password-reset-journey.cy.ts - Password reset workflow"
        echo "  05-profile-journey.cy.ts        - Profile management and updates"
        echo "  06-ballot-journey.cy.ts         - Ballot purchase and assignment"
        echo "  07-closed-draws-journey.cy.ts   - Viewing closed draws and results"
        echo "  99-demo.cy.ts                   - Complete demo journey for product owner"
        echo ""
        echo "Test Environment Features:"
        echo "  - SQLite database (faster than PostgreSQL)"
        echo "  - Celery tasks run eagerly (no background workers)"
        echo "  - Email sent to console (no external email service)"
        echo "  - Separate port (8081) to avoid conflicts"
        echo "  - Optimized for speed and isolation"
        echo ""
        echo "Examples:"
        echo "  $0 setup         # Set up the test environment"
        echo "  $0 full-test     # Run all tests (backend + frontend)"
        echo "  $0 backend-check # Run all backend checks"
        echo "  $0 all           # Run all Cypress tests"
        echo "  $0 interactive   # Open Cypress UI"
        echo "  $0 clean         # Clean up test environment"
        ;;
esac 
