docker exec spark-client /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/experiments/pipelines/streaming_ingestion.py \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://postgres:5432/postgres \
  admin \
  postgrespassword \
  public.yellow_tripdata \
  bronze.yellow_tripdata


docker exec spark-client /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/experiments/pipelines/batch_ingestion.py \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://datasource_postgres:5432/postgres \
  admin \
  postgrespassword \
  public.yellow_tripdata \
  bronze.yellow_tripdata \
  "2025-02-01 00"

docker exec spark-client /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/experiments/pipelines/batch_ingestion.py \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://datasource_postgres:5432/postgres \
  admin \
  postgrespassword \
  public.yellow_tripdata \
  bronze.yellow_tripdata \
  NONE

docker exec spark-client /opt/spark/bin/spark-submit \
  --class datagate.experiment.streaming.streaming_ingestion_ps_to_bronze_layer \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/experiments/ingest_data-1.0.jar \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://postgres:5432/postgres \
  admin \
  postgrespassword \
  public.yellow_tripdata \
  bronze.yellow_tripdata


docker exec spark-client /opt/spark/bin/spark-submit \
  --class datagate.experiment.batch.batch_ingestion_from_ps_to_bronze_layer \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/experiments/ingest_data-1.0.jar \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://datasource_postgres:5432/postgres \
  admin \
  postgrespassword \
  public.yellow_tripdata \
  bronze.yellow_tripdata \
  "2025-02-01 00"

docker exec spark-master /opt/spark/bin/spark-submit \
  --class datagate.experiment.batch.batch_ingestion_from_ps_to_bronze_layer \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/experiments/ingest_data-1.0.jar \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  jdbc:postgresql://datasource_postgres:5432/postgres \
  admin \
  postgrespassword \
  public.yellow_tripdata \
  bronze.yellow_tripdata_scala \
  NONE


  docker exec spark-client /opt/spark/bin/spark-submit \
  --class datagate.profiling.profiling \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/datagate/computes-1.0.jar \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  silver.silver_yellow_tripdata \
  "2025-01-01 00:00:00" \
  "2025-01-01 01:00:00" \
  jdbc:postgresql://datagate_database:5432/datagate \
  admin \
  datagatepassword

docker exec spark-client /opt/spark/bin/spark-submit \
  --class datagate.rules_suggestion.rules_suggestion \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/datagate/computes-1.0.jar \
  http://iceberg-rest:8181 \
  http://minio:9000 \
  admin \
  miniopassword \
  us-east-1 \
  silver.silver_yellow_tripdata \
  "2025-01-01 00:00:00" \
  "2025-01-01 01:00:00" \
  jdbc:postgresql://datagate_database:5432/datagate \
  admin \
  datagatepassword
