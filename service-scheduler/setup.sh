#!/bin/bash

# Service Scheduler Setup Script
echo "🚀 Setting up Service Scheduler Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the service-scheduler root directory"
    exit 1
fi

print_info "Starting database and Hasura services..."

# Start database services
docker-compose up -d postgres redis hasura

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 10

# Check if services are running
if ! docker-compose ps | grep -q "postgres.*Up"; then
    print_error "PostgreSQL failed to start"
    exit 1
fi

if ! docker-compose ps | grep -q "hasura.*Up"; then
    print_error "Hasura failed to start"
    exit 1
fi

print_status "Database services are running"

# Backend setup
print_info "Setting up Python backend..."
cd backend

# Check if this is an existing installation with old venv
if [ -d "venv" ]; then
    print_warning "Found old pip-based virtual environment. This project now uses uv."
    print_info "Run './migrate-to-uv.sh' to migrate, or remove 'venv/' manually."
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_warning "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Install Python dependencies with uv
print_info "Installing Python dependencies with uv..."
uv sync

print_status "Backend setup complete"

# Return to root directory
cd ..

# Frontend setup
print_info "Setting up Angular frontend..."
cd frontend

# Install Node.js dependencies (if not already installed)
if [ ! -d "node_modules" ]; then
    print_info "Installing Node.js dependencies..."
    npm install
fi

print_status "Frontend setup complete"

# Return to root directory
cd ..

print_status "Application setup complete!"

echo ""
echo "🎉 Service Scheduler is ready!"
echo ""
echo "To start the application:"
echo ""
echo "${BLUE}1. Start the backend:${NC}"
echo "   cd backend"
echo "   uv run uvicorn main:app --reload"
echo ""
echo "${BLUE}2. Start the frontend (in a new terminal):${NC}"
echo "   cd frontend"
echo "   ng serve"
echo ""
echo "${BLUE}3. Access the application:${NC}"
echo "   Frontend: http://localhost:4200"
echo "   Backend API: http://localhost:8000"
echo "   Hasura Console: http://localhost:8080"
echo ""
echo "${BLUE}Default admin credentials:${NC}"
echo "   Email: admin@example.com"
echo "   Password: admin123"
echo ""
echo "${GREEN}Happy coding! 🚀${NC}"
