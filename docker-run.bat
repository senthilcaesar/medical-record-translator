@echo off
setlocal enabledelayedexpansion

:: Function to display help message
:show_help
    echo Usage: docker-run.bat [OPTION]
    echo Run the Medical Record Translator application using Docker
    echo.
    echo Options:
    echo   dev         Run in development mode with hot reloading
    echo   prod        Run in production mode
    echo   build       Build the Docker images
    echo   down        Stop and remove containers
    echo   logs        Show logs from all containers
    echo   help        Display this help message
    echo.
    goto :eof

:: Check if .env file exists for production
:check_env_file
    if not exist .env (
        echo Error: .env file not found!
        echo Please create a .env file based on .env.prod.example
        exit /b 1
    )
    goto :eof

:: Process command line arguments
if "%1"=="" goto show_help

if "%1"=="dev" (
    echo Starting in development mode...
    docker-compose up
    goto :eof
)

if "%1"=="prod" (
    call :check_env_file
    echo Starting in production mode...
    docker-compose -f docker-compose.prod.yml up -d
    goto :eof
)

if "%1"=="build" (
    if "%2"=="prod" (
        call :check_env_file
        echo Building production images...
        docker-compose -f docker-compose.prod.yml build
    ) else (
        echo Building development images...
        docker-compose build
    )
    goto :eof
)

if "%1"=="down" (
    if "%2"=="prod" (
        echo Stopping production containers...
        docker-compose -f docker-compose.prod.yml down
    ) else (
        echo Stopping development containers...
        docker-compose down
    )
    goto :eof
)

if "%1"=="logs" (
    if "%2"=="prod" (
        echo Showing production logs...
        docker-compose -f docker-compose.prod.yml logs -f
    ) else (
        echo Showing development logs...
        docker-compose logs -f
    )
    goto :eof
)

if "%1"=="help" (
    goto show_help
) else (
    goto show_help
)