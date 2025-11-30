#!/bin/bash

# ProductMaker Docker Utility Script
# Helper script to manage docker containers

function show_help {
    echo "ProductMaker Docker Utilities"
    echo ""
    echo "Usage: ./docker-util.sh [command] [service]"
    echo ""
    echo "Commands:"
    echo "  bash [app|db]    - Open a bash shell in the specified container"
    echo "                     (defaults to 'app' if no service specified)"
    echo "  logs [app|db]    - Tail logs for the specified container"
    echo "                     (shows all logs if no service specified)"
    echo "  psql             - Open psql shell in the db container"
    echo "  restart          - Restart all services"
    echo "  stop             - Stop all services"
    echo "  --help, -h       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker-util.sh bash app"
    echo "  ./docker-util.sh logs db"
    echo "  ./docker-util.sh psql"
}

if [ "$1" == "bash" ]; then
    if [ "$2" == "db" ]; then
        docker exec -it productmaker-db-1 bash
    else
        docker exec -it productmaker-app-1 bash
    fi
elif [ "$1" == "logs" ]; then
    if [ -z "$2" ]; then
        docker compose logs -f
    else
        docker compose logs -f $2
    fi
elif [ "$1" == "psql" ]; then
    docker exec -it productmaker-db-1 psql -U postgres -d productmaker
elif [ "$1" == "restart" ]; then
    docker compose restart
elif [ "$1" == "stop" ]; then
    docker compose down
elif [ "$1" == "--help" ] || [ "$1" == "-h" ] || [ "$1" == "help" ]; then
    show_help
else
    show_help
fi
