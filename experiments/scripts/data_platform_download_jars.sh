#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define the target directory for jars relative to the script location
TARGET_DIR="$SCRIPT_DIR/../data_platform/compute_engine/spark/custom_jars"

# Create the directory if it doesn't exist
mkdir -p "$TARGET_DIR"

echo "Downloading jars to $TARGET_DIR..."

# 1. Iceberg Spark Runtime (Enables Iceberg tables in Spark)
echo "Downloading iceberg-spark-runtime-3.5_2.12-1.10.1.jar..."
curl -L -o "$TARGET_DIR/iceberg-spark-runtime-3.5_2.12-1.10.1.jar" https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar

# 2. PostgreSQL JDBC Driver (For connecting to Postgres-based catalogs like REST Catalog backend)
echo "Downloading postgresql-42.7.10.jar..."
curl -L -o "$TARGET_DIR/postgresql-42.7.10.jar" https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar

# 3. Hadoop AWS (Required for S3A file system support)
# Spark 3.5 uses Hadoop 3.3.4 by default
echo "Downloading hadoop-aws-3.3.4.jar..."
curl -L -o "$TARGET_DIR/hadoop-aws-3.3.4.jar" https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar

# 4. AWS Java SDK Bundle (Dependency for Hadoop AWS)
# Version 1.12.262 creates a compatible pair with hadoop-aws 3.3.4
echo "Downloading aws-java-sdk-bundle-1.12.262.jar..."
curl -L -o "$TARGET_DIR/aws-java-sdk-bundle-1.12.262.jar" https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

echo "All downloads complete!"
ls -lh "$TARGET_DIR"
