#!/bin/bash

# Setup platform
docker network create datagate_net --driver bridge

# Setup minio
cd ../data_platform/storage/minio
docker compose up -d
