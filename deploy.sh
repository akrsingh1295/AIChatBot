#!/bin/bash

# Production Deployment Script for AI ChatBot
# Usage: ./deploy.sh [environment]

set -e  # Exit on any error

ENVIRONMENT=${1:-production}
echo "🚀 Deploying AI ChatBot to $ENVIRONMENT environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from template..."
        cp env.production.template .env
        log_warning "Please edit .env file with your configuration before continuing."
        read -p "Press Enter when you've configured the .env file..."
    fi
    
    log_success "Prerequisites check completed"
}

# Build and deploy
deploy() {
    log_info "Building Docker images..."
    docker-compose build --no-cache
    
    log_info "Starting services..."
    docker-compose up -d
    
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Health checks
    log_info "Running health checks..."
    
    # Check backend health
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Check frontend health
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
}

# Cleanup old containers and images
cleanup() {
    log_info "Cleaning up old containers and images..."
    docker-compose down
    docker system prune -f
    log_success "Cleanup completed"
}

# Show logs
show_logs() {
    log_info "Showing application logs..."
    docker-compose logs -f
}

# Main deployment flow
main() {
    echo "🤖 AI ChatBot Production Deployment"
    echo "=================================="
    
    case ${1:-deploy} in
        "deploy")
            check_prerequisites
            deploy
            log_success "🎉 Deployment completed successfully!"
            log_info "Your chatbot is now running at:"
            log_info "  Frontend: http://localhost"
            log_info "  Backend API: http://localhost:8000"
            log_info "  API Docs: http://localhost:8000/docs"
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            show_logs
            ;;
        "restart")
            log_info "Restarting services..."
            docker-compose restart
            log_success "Services restarted"
            ;;
        "stop")
            log_info "Stopping services..."
            docker-compose down
            log_success "Services stopped"
            ;;
        "status")
            log_info "Service status:"
            docker-compose ps
            ;;
        *)
            echo "Usage: $0 [deploy|cleanup|logs|restart|stop|status]"
            echo "  deploy  - Build and deploy the application (default)"
            echo "  cleanup - Clean up old containers and images"
            echo "  logs    - Show application logs"
            echo "  restart - Restart all services"
            echo "  stop    - Stop all services"
            echo "  status  - Show service status"
            exit 1
            ;;
    esac
}

main "$@" 