#!/bin/sh

# Run database migrations
refinery migrate -c refinery.toml

# Start the application
./headless-api
