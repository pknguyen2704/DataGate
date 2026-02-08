#!/bin/bash

# Setup platform
docker network create datagate_net --driver bridge
docker network create platform_net --driver bridge
