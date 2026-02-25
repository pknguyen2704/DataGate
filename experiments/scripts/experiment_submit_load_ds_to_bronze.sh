#!/bin/bash
set -euo pipefail

# Usage:
# ./experiment_submit_load_ds_to_bronze.sh --sourceTable yellow_tripdata --targetNamespace bronze --mode append


# ---- Runtime config (from env or defaults) ----
S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}"
AWS_REGION="${S3_REGION:-${AWS_REGION:-us-east-1}}"
WAREHOUSE="${ICEBERG_WAREHOUSE:-s3://lakehouse/}"

BUCKET="${WAREHOUSE#s3://}"
BUCKET="${BUCKET%%/*}"

JAR_IN_CONTAINER="/opt/spark/jobs/experiment_jobs-1.0.jar"

echo "---------------------------------------------"
echo "Submit Config:"
echo "  S3 endpoint:  ${S3_ENDPOINT}"
echo "  AWS region:   ${AWS_REGION}"
echo "  Warehouse:    ${WAREHOUSE}"
echo "  Bucket:       ${BUCKET}"
echo "  Jar:          ${JAR_IN_CONTAINER}"
echo "  Args:         $*"
echo "---------------------------------------------"

# ---- Submit ----
echo "Submitting Spark Job: Load_From_DS_To_Bronze..."

docker exec data_platform_spark_client /opt/spark/bin/spark-submit \
  --class pknguyen.datagate.Load_from_ds_to_lakehouse \
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