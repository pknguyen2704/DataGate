#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

chmod +x ./experiments/scripts/*.sh
docker network create datagate_net --driver bridge
