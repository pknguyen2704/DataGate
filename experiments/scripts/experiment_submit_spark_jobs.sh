echo "Submitting Spark Job: Load_From_DS_To_Bronze..."

docker exec data_platform_spark_client /opt/spark/bin/spark-submit \
  --class pknguyen.date_gate.Load_From_DS_To_Bronze \
  --master spark://data-platform-spark-master:7077 \
  --deploy-mode client \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/jobs/java/java_spark_jobs-1.0-SNAPSHOT.jar