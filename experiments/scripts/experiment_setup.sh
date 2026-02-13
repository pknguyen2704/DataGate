#!/bin/bash

# Setup platform
docker network create data_gate_net --driver bridge
docker network create data_platform_net --driver bridge
