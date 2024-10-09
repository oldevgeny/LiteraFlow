#!/bin/bash

# Apply database migrations
poetry run python literaflow/main.py

# Start the server
exec "$@"
