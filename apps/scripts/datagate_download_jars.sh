#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define the target directory for jars relative to the script location
TARGET_DIR="$SCRIPT_DIR/../infra/compute_engine/spark/custom_jars"

# Create the directory if it doesn't exist
mkdir -p "$TARGET_DIR"

echo "Downloading jars to $TARGET_DIR..."

# 1. Iceberg Spark Runtime (Enables Iceberg tables in Spark)
echo "Downloading iceberg-spark-runtime-3.5_2.12-1.10.1.jar..."
curl -L -o "$TARGET_DIR/iceberg-spark-runtime-3.5_2.12-1.10.1.jar" https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar

# 2. PostgreSQL JDBC Driver (For connecting to Postgres-based catalogs like REST Catalog backend)
echo "Downloading postgresql-42.7.10.jar..."
curl -L -o "$TARGET_DIR/postgresql-42.7.10.jar" https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar
# 3. Iceberg AWS (Enables S3 support in Iceberg, required if using S3 as storage for Iceberg tables)
echo "Downloading iceberg-aws-1.10.1.jar..."
curl -L -o "$TARGET_DIR/iceberg-aws-1.10.1.jar" https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws/1.10.1/iceberg-aws-1.10.1.jar

# 4. AWS SDK v2 (Dependency for Iceberg AWS Bundle)
echo "Downloading aws-sdk-java-v2-2.41.34.jar..."
curl -L -o "$TARGET_DIR/aws-sdk-java-v2-2.41.34.jar" https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.41.34/bundle-2.41.34.jar

# 5. Deequ (Data quality library from AWS, useful for data validation in Spark)
echo "Downloading deequ-2.0.13-spark-3.5.jar..."
curl -L -o "$TARGET_DIR/deequ-2.0.13-spark-3.5.jar" https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.13-spark-3.5/deequ-2.0.13-spark-3.5.jar

echo "All downloads complete!"
ls -lh "$TARGET_DIR"
