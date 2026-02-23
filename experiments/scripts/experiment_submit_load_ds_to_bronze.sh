#!/bin/bash
set -euo pipefail

# Usage:
# ./experiment_submit_load_ds_to_bronze.sh --sourceTable yellow_tripdata --targetNamespace bronze --mode append

# ---- Local jar check (optional, just warn) ----
LOCAL_JAR_PATH="/Users/andrew/Dev/DataGate/experiments/jobs/java_spark_jobs/target/java_spark_jobs-1.0-SNAPSHOT.jar"
if [ ! -f "$LOCAL_JAR_PATH" ]; then
  echo "Warning: local JAR not found at $LOCAL_JAR_PATH (this is OK if jar is already inside spark_client)."
fi

# ---- Runtime config (from env or defaults) ----
S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}"
AWS_REGION="${S3_REGION:-${AWS_REGION:-us-east-1}}"
WAREHOUSE="${ICEBERG_WAREHOUSE:-s3://lakehouse/}"

BUCKET="${WAREHOUSE#s3://}"
BUCKET="${BUCKET%%/*}"

JAR_IN_CONTAINER="/opt/spark/jobs/java/java_spark_jobs-1.0-SNAPSHOT.jar"

echo "---------------------------------------------"
echo "Submit Config:"
echo "  S3 endpoint:  ${S3_ENDPOINT}"
echo "  AWS region:   ${AWS_REGION}"
echo "  Warehouse:    ${WAREHOUSE}"
echo "  Bucket:       ${BUCKET}"
echo "  Jar:          ${JAR_IN_CONTAINER}"
echo "  Args:         $*"
echo "---------------------------------------------"

# ---- Check jar exists in spark client container ----
if ! docker exec data_platform_spark_client sh -lc "[ -f '${JAR_IN_CONTAINER}' ]"; then
  echo "ERROR: JAR not found inside container: ${JAR_IN_CONTAINER}"
  echo "Fix: copy/bind jar into spark_client at /opt/spark/jobs/java/"
  exit 1
fi

# ---- Submit ----
echo "Submitting Spark Job: Load_From_DS_To_Bronze..."

docker exec data_platform_spark_client /opt/spark/bin/spark-submit \
  --class pknguyen.date_gate.Load_From_DS_To_Bronze \
  --master spark://data-platform-spark-master:7077 \
  --deploy-mode client \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  \
  --conf "spark.driverEnv.AWS_REGION=${AWS_REGION}" \
  --conf "spark.driverEnv.AWS_DEFAULT_REGION=${AWS_REGION}" \
  --conf "spark.executorEnv.AWS_REGION=${AWS_REGION}" \
  --conf "spark.executorEnv.AWS_DEFAULT_REGION=${AWS_REGION}" \
  --conf "spark.driver.extraJavaOptions=-Daws.region=${AWS_REGION} -Daws.default.region=${AWS_REGION}" \
  --conf "spark.executor.extraJavaOptions=-Daws.region=${AWS_REGION} -Daws.default.region=${AWS_REGION}" \
  \
  --conf "spark.hadoop.fs.s3a.endpoint=${S3_ENDPOINT}" \
  --conf "spark.hadoop.fs.s3a.path.style.access=true" \
  --conf "spark.hadoop.fs.s3a.connection.ssl.enabled=false" \
  --conf "spark.hadoop.fs.s3a.access.key=${MINIO_ROOT_USER:-admin}" \
  --conf "spark.hadoop.fs.s3a.secret.key=${MINIO_ROOT_PASSWORD:-miniopassword}" \
  --conf "spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider" \
  \
  "$JAR_IN_CONTAINER" \
  "$@"