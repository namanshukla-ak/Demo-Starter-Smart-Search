#!/bin/bash

# Docker commands for Neurologix Smart Search POV

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_color $BLUE "🐳 Neurologix Smart Search - Docker Management"

# Function to show usage
show_usage() {
    echo "Usage: ./docker.sh [command]"
    echo ""
    echo "Commands:"
    echo "  dev       - Start development environment (both frontend & backend)"
    echo "  backend   - Start only backend service"
    echo "  frontend  - Start only frontend service"
    echo "  prod      - Start production environment"
    echo "  db        - Start MySQL database only"
    echo "  full      - Start everything (app + database + redis)"
    echo "  build     - Build all Docker images"
    echo "  stop      - Stop all services"
    echo "  clean     - Stop and remove all containers, images, and volumes"
    echo "  logs      - View logs from all services"
    echo "  shell     - Open shell in development container"
    echo ""
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    print_color $RED "❌ Docker and docker-compose are required but not installed."
    exit 1
fi

# Use docker compose or docker-compose based on what's available
DOCKER_COMPOSE="docker-compose"
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
fi

# Parse command
case "${1:-help}" in
    dev|development)
        print_color $GREEN "🚀 Starting development environment..."
        $DOCKER_COMPOSE --profile dev up --build
        ;;
    
    backend)
        print_color $GREEN "🔧 Starting backend service..."
        $DOCKER_COMPOSE --profile backend up --build
        ;;
    
    frontend)
        print_color $GREEN "🎨 Starting frontend service..."
        $DOCKER_COMPOSE --profile frontend up --build
        ;;
    
    prod|production)
        print_color $GREEN "🏭 Starting production environment..."
        $DOCKER_COMPOSE --profile prod up --build -d
        print_color $GREEN "✅ Production environment started!"
        print_color $YELLOW "Frontend: http://localhost:8501"
        print_color $YELLOW "Backend: http://localhost:8000"
        ;;
    
    db|database)
        print_color $GREEN "🗄️ Starting MySQL database..."
        $DOCKER_COMPOSE --profile db up -d
        ;;
    
    full)
        print_color $GREEN "🌟 Starting full environment..."
        $DOCKER_COMPOSE --profile full up --build
        ;;
    
    build)
        print_color $GREEN "🔨 Building Docker images..."
        $DOCKER_COMPOSE build
        ;;
    
    stop)
        print_color $YELLOW "⏹️ Stopping all services..."
        $DOCKER_COMPOSE down
        ;;
    
    clean)
        print_color $RED "🧹 Cleaning up Docker environment..."
        $DOCKER_COMPOSE down -v --rmi all
        docker system prune -f
        print_color $GREEN "✅ Cleanup complete!"
        ;;
    
    logs)
        print_color $BLUE "📋 Viewing logs..."
        $DOCKER_COMPOSE logs -f
        ;;
    
    shell)
        print_color $BLUE "🐚 Opening shell in development container..."
        $DOCKER_COMPOSE --profile dev exec neurologix-dev bash
        ;;
    
    help|--help|-h)
        show_usage
        ;;
    
    *)
        print_color $RED "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
