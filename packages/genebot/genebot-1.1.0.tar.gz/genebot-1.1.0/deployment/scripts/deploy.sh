#!/bin/bash
set -e

# Trading Bot Deployment Script
# Usage: ./deploy.sh [environment] [action]

ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    ENV_FILE="$PROJECT_ROOT/deployment/environments/.env.$ENVIRONMENT"
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file not found: $ENV_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Load environment configuration
load_environment() {
    log_info "Loading environment configuration for: $ENVIRONMENT"
    
    # Source environment file
    set -a
    source "$PROJECT_ROOT/deployment/environments/.env.$ENVIRONMENT"
    set +a
    
    # Validate configuration
    python3 "$PROJECT_ROOT/deployment/config_loader.py" "$ENVIRONMENT"
    
    if [[ $? -ne 0 ]]; then
        log_error "Configuration validation failed"
        exit 1
    fi
    
    log_success "Environment configuration loaded"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build production image
    docker build -t trading-bot:latest -t "trading-bot:$ENVIRONMENT" .
    
    if [[ $? -ne 0 ]]; then
        log_error "Docker build failed"
        exit 1
    fi
    
    log_success "Docker images built successfully"
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."
    
    cd "$PROJECT_ROOT"
    
    # Create necessary directories
    mkdir -p logs/{errors,trades,metrics}
    mkdir -p data/backups
    
    # Set proper permissions
    chmod 755 logs
    chmod 755 data
    
    # Deploy with Docker Compose
    if [[ "$ENVIRONMENT" == "development" ]]; then
        docker-compose -f docker-compose.dev.yml up -d
    else
        docker-compose up -d
    fi
    
    if [[ $? -ne 0 ]]; then
        log_error "Deployment failed"
        exit 1
    fi
    
    log_success "Application deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Wait for services to start
    sleep 30
    
    # Check application health
    HEALTH_URL="http://localhost:8080/health"
    
    for i in {1..10}; do
        if curl -f "$HEALTH_URL" &> /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        log_warning "Health check attempt $i failed, retrying in 10 seconds..."
        sleep 10
    done
    
    log_error "Health check failed after 10 attempts"
    return 1
}

# Rollback deployment
rollback() {
    log_warning "Rolling back deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop current deployment
    docker-compose down
    
    # Restore from backup (if available)
    if [[ -f "docker-compose.backup.yml" ]]; then
        mv docker-compose.backup.yml docker-compose.yml
        docker-compose up -d
        log_success "Rollback completed"
    else
        log_error "No backup found for rollback"
        exit 1
    fi
}

# Backup current deployment
backup_deployment() {
    log_info "Creating deployment backup..."
    
    cd "$PROJECT_ROOT"
    
    # Backup docker-compose file
    if [[ -f "docker-compose.yml" ]]; then
        cp docker-compose.yml "docker-compose.backup.yml"
    fi
    
    # Backup database
    if [[ "$ENVIRONMENT" != "development" ]]; then
        docker-compose exec -T postgres pg_dump -U tradingbot tradingbot > "data/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    fi
    
    log_success "Backup created"
}

# Stop application
stop_application() {
    log_info "Stopping application..."
    
    cd "$PROJECT_ROOT"
    docker-compose down
    
    log_success "Application stopped"
}

# Show logs
show_logs() {
    log_info "Showing application logs..."
    
    cd "$PROJECT_ROOT"
    docker-compose logs -f trading-bot
}

# Main execution
main() {
    log_info "Starting deployment process for environment: $ENVIRONMENT"
    log_info "Action: $ACTION"
    
    case "$ACTION" in
        "deploy")
            check_prerequisites
            load_environment
            backup_deployment
            build_images
            deploy_application
            health_check
            ;;
        "rollback")
            rollback
            ;;
        "stop")
            stop_application
            ;;
        "logs")
            show_logs
            ;;
        "health")
            health_check
            ;;
        *)
            echo "Usage: $0 [environment] [deploy|rollback|stop|logs|health]"
            echo "Environments: development, staging, production"
            exit 1
            ;;
    esac
    
    log_success "Deployment process completed successfully"
}

# Execute main function
main "$@"