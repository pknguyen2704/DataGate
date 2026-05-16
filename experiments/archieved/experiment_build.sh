#!/bin/bash
set -e

echo "[DataGate] Building Experiments jobs..."

# Đi vào thư mục project
cd ../jobs/experiment_jobs

# Build
mvn clean package -DskipTests

echo "[DataGate] Copying jar to functions root..."

# Copy jar ra ngoài thư mục functions/
cp target/*.jar ..

echo "[DataGate] Build completed."