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

# Optional: filter by date_hour
echo ""
echo -e "${YELLOW}Enter date_hour filter (format: YYYY-MM-DD HH:00:00) or leave blank to load all:${NC}"
read -p "> " date_hour_input
DATE_HOUR="${date_hour_input:-}"

# Display selected configuration
echo ""
echo -e "${GREEN}Selected Configuration:${NC}"
echo "  Source Table:      $TABLE_NAME"
echo "  Target Table:      $TABLE_TARGET"
if [ -z "$DATE_HOUR" ]; then
  echo "  Date Hour Filter:  (none - loading all data)"
else
  echo "  Date Hour Filter:  $DATE_HOUR"
fi
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

if [ -z "$DATE_HOUR" ]; then
  docker exec experiments_data_platform_spark_client /opt/spark/bin/spark-submit \
    --class pknguyen.datagate.Load_from_ds_to_lakehouse \
    --master spark://data-platform-spark-master:7077 \
    --deploy-mode client \
    --driver-memory 2G \
    --executor-memory 4G \
    --executor-cores 2 \
    /opt/spark/jobs/experiment_jobs-1.0.jar \
    "$TABLE_NAME" "$TABLE_TARGET"
else
  docker exec experiments_data_platform_spark_client /opt/spark/bin/spark-submit \
    --class pknguyen.datagate.Load_from_ds_to_lakehouse \
    --master spark://data-platform-spark-master:7077 \
    --deploy-mode client \
    --driver-memory 2G \
    --executor-memory 4G \
    --executor-cores 2 \
    /opt/spark/jobs/experiment_jobs-1.0.jar \
    "$TABLE_NAME" "$TABLE_TARGET" "$DATE_HOUR"
fi

echo ""
echo -e "${GREEN}Job submission complete.${NC}"