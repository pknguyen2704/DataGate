#!/bin/bash
set -e

echo "[DataGate] Building Maven project..."

# Đi vào thư mục project
cd ../functions/datagate

# Build
mvn clean package -DskipTests

echo "[DataGate] Copying jar to functions root..."

# Copy jar ra ngoài thư mục functions/
cp target/datagate-1.0.jar ..

echo "[DataGate] Build completed."