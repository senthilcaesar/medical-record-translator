#!/bin/bash

# Function to display help message
show_help() {
    echo "Usage: ./docker-run.sh [OPTION]"
    echo "Run the Medical Record Translator application using Docker"
    echo ""
    echo "Options:"
    echo "  dev         Run in development mode with hot reloading"
    echo "  prod        Run in production mode"
    echo "  build       Build the Docker images"
    echo "  down        Stop and remove containers"
    echo "  logs        Show logs from all containers"
    echo "  help        Display this help message"
    echo ""
}

# Check if .env file exists for production
check_env_file() {
    if [ ! -f .env ]; then
        echo "Error: .env file not found!"
        echo "Please create a .env file based on .env.prod.example"
        exit 1
    fi
}

# Process command line arguments
case "$1" in
    dev)
        echo "Starting in development mode..."
        docker-compose up
        ;;
    prod)
        check_env_file
        echo "Starting in production mode..."
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    build)
        case "$2" in
            prod)
                check_env_file
                echo "Building production images..."
                docker-compose -f docker-compose.prod.yml build
                ;;
            *)
                echo "Building development images..."
                docker-compose build
                ;;
        esac
        ;;
    down)
        case "$2" in
            prod)
                echo "Stopping production containers..."
                docker-compose -f docker-compose.prod.yml down
                ;;
            *)
                echo "Stopping development containers..."
                docker-compose down
                ;;
        esac
        ;;
    logs)
        case "$2" in
            prod)
                echo "Showing production logs..."
                docker-compose -f docker-compose.prod.yml logs -f
                ;;
            *)
                echo "Showing development logs..."
                docker-compose logs -f
                ;;
        esac
        ;;
    help|*)
        show_help
        ;;
esac