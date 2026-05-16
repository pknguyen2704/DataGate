#!/bin/bash

# Get all running container IDs
container_ids=$(docker ps -q)

if [ -n "$container_ids" ]; then
    echo "Stopping containers..."
    docker stop $container_ids
    echo "Stopped all running containers."
else
    echo "No running containers found."
fi
