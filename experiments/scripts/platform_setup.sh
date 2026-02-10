#!/bin/bash

# Setup platform
docker network create datagate-net --driver bridge
docker network create data-platform-net --driver bridge
