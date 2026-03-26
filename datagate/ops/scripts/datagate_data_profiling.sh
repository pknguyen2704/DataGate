echo "[DataGate] Data Profiling..."

docker exec datagate_spark_client /opt/spark/bin/spark-submit \
  --class pknguyen.datagate.data_profiling \
  --master spark://datagate-spark-master:7077 \
  --deploy-mode cluster \
  --driver-memory 2G \
  --executor-memory 4G \
  --executor-cores 2 \
  /opt/spark/work-dir/functions/datagate-functions-1.0.jar

echo "[DataGate] Data Profiling job completed"