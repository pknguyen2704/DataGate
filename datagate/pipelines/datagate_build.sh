#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "[DataGate] Building Maven project datagate-functions..."

cd "$SCRIPT_DIR/datagate-functions"

mvn clean package -DskipTests

echo "[DataGate] Copying jar to pipelines root..."
cp target/*.jar "$SCRIPT_DIR/"

echo "[DataGate] Build completed successfully."
