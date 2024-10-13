#!/bin/bash

# Apply database migrations
poetry run python main.py

# Start the server
exec "$@"
