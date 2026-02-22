#!/bin/bash

# Check if JAR exists
JAR_PATH="/Users/andrew/Dev/DataGate/experiments/jobs/java_spark_jobs/target/java_spark_jobs-1.0-SNAPSHOT.jar"
if [ ! -f "$JAR_PATH" ]; then
    echo "Warning: JAR file not found at $JAR_PATH. Please run 'mvn package' in 'experiments/jobs/java_spark_jobs' first."
fi

# Submit the job with arguments passed to the script
echo "Submitting Spark Job: Load_From_DS_To_Bronze..."
echo "Arguments: $@"

docker exec data_platform_spark_client /opt/spark/bin/spark-submit \
  --class pknguyen.date_gate.Load_From_DS_To_Bronze \
  --master spark://data-platform-spark-master:7077 \
  --deploy-mode client \
  --driver-memory 1G \
  --executor-memory 2G \
  --executor-cores 2 \
  --conf spark.sql.shuffle.partitions=32 \
  --conf spark.default.parallelism=32 \
  /opt/spark/jobs/java/java_spark_jobs-1.0-SNAPSHOT.jar \
  "$@"
