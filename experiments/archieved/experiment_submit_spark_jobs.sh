#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Available tables in the data source
TABLES=("yellow_tripdata" "green_tripdata")

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Spark Job Submission - Load to Bronze${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Select source table from PostgreSQL
echo -e "${YELLOW}Select source table from PostgreSQL:${NC}"
for i in "${!TABLES[@]}"; do
  echo "$((i+1)). ${TABLES[$i]}"
done
read -p "Enter choice (1-${#TABLES[@]}) [default: 1]: " table_choice
table_choice=${table_choice:-1}

if [[ $table_choice -ge 1 && $table_choice -le ${#TABLES[@]} ]]; then
  TABLE_NAME="${TABLES[$((table_choice-1))]}"
else
  echo -e "${YELLOW}Invalid choice. Using default: yellow_tripdata${NC}"
  TABLE_NAME="yellow_tripdata"
fi

# Select target Iceberg table
echo ""
echo -e "${YELLOW}Enter target Iceberg table name [default: $TABLE_NAME]: ${NC}"
read -p "> " table_target
TABLE_TARGET="${table_target:-$TABLE_NAME}"

# Display selected configuration
echo ""
echo -e "${GREEN}Selected Configuration:${NC}"
echo "  Source Table:      $TABLE_NAME"
echo "  Target Table:      $TABLE_TARGET"
echo ""

read -p "Proceed with submission? (y/n) [default: y]: " proceed
proceed=${proceed:-y}

if [[ $proceed != "y" && $proceed != "Y" ]]; then
  echo "Cancelled."
  exit 0
fi

# Build spark-submit command
echo ""
echo -e "${BLUE}Submitting Spark Job: Load_from_ds_to_lakehouse...${NC}"

docker exec spark-client /opt/spark/bin/spark-submit \
  --class datagate.experiment.batch.batch_ingestion_from_ps_to_bronze_layer \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.rest=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.rest.catalog-impl=org.apache.iceberg.rest.RESTCatalog \
  --conf spark.sql.catalog.rest.uri=http://iceberg-rest:8181 \
  --conf spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.iceberg.catalog-impl=org.apache.iceberg.rest.RESTCatalog \
  --conf spark.sql.catalog.iceberg.uri=http://iceberg-rest:8181 \
  /opt/spark/work-dir/experiments/ingest_data-1.0.jar \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://postgres:5432/postgres \
  admin \
  postgrespassword \
  "public.$TABLE_NAME" \
  "bronze.$TABLE_TARGET" \
  append

echo ""
echo -e "${GREEN}Job submission complete.${NC}"