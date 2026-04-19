import sys
import os
from pyspark.sql import SparkSession, functions as F
from pydeequ.analyzers import AnalysisRunner, AnalyzerContext, Completeness, Uniqueness, Mean, Minimum, Maximum, StandardDeviation, Correlation
import datetime
import psycopg2

def main():
    if len(sys.argv) < 5:
        print("Usage: datagate_deequ_analysis.py <catalog> <schema> <table> <snapshot_time>")
        sys.exit(1)

    catalog = sys.argv[1]
    schema = sys.argv[2]
    table = sys.argv[3]
    snapshot_time_str = sys.argv[4]
    
    full_table_name = f"{schema}.{table}"
    
    # Configure Spark for Iceberg and PyDeequ
    # Note: pydeequ requires deequ jar. Ensure it's in the spark submit conf.
    spark = SparkSession.builder \
        .appName(f"DataGate-Deequ-Analysis-{full_table_name}") \
        .getOrCreate()

    # Load data from Iceberg
    df = spark.table(f"{catalog}.{schema}.{table}")
    
    print(f"Starting Deequ analysis for {full_table_name}...")

    # Define analyzers based on column types
    analysis_runner = AnalysisRunner(spark).onData(df)
    
    # Common metrics for all columns
    for col_name, dtype in df.dtypes:
        analysis_runner.addAnalyzer(Completeness(col_name))
        
        # Numeric metrics
        if dtype in ['int', 'bigint', 'double', 'float', 'decimal']:
            analysis_runner.addAnalyzer(Mean(col_name))
            analysis_runner.addAnalyzer(Minimum(col_name))
            analysis_runner.addAnalyzer(Maximum(col_name))
            analysis_runner.addAnalyzer(StandardDeviation(col_name))
            
    # Add uniqueness for potential ID columns (simplified logic)
    # In real world, might want to only do this for PKs
    # analysis_runner.addAnalyzer(Uniqueness(["id"]))

    analysis_result = analysis_runner.run()
    result_df = AnalyzerContext.successMetricsAsDataFrame(spark, analysis_result)
    
    # Process results
    metrics = result_df.collect()
    
    print(f"Analysis complete. Found {len(metrics)} metrics. Persisting to Postgres...")

    # Postgres connection info (should be passed via environment variables in production)
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_db = os.getenv("POSTGRES_DB", "datagate")
    pg_user = os.getenv("POSTGRES_USER", "admin")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "datagatepassword")

    conn = psycopg2.connect(
        host=pg_host,
        database=pg_db,
        user=pg_user,
        password=pg_pass
    )
    cur = conn.cursor()

    try:
        for row in metrics:
            # entity: Column, instance: col_name, name: metric_name, value: metric_value
            # Note: entity can be 'Dataset' for global metrics
            entity = row['entity']
            instance = row['instance']
            metric_name = row['name']
            value = row['value']
            
            cur.execute(
                """
                INSERT INTO dg_observability_metrics (table_name, column_name, metric_name, metric_value, snapshot_time)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (full_table_name, instance if entity == 'Column' else '*', metric_name, value, snapshot_time_str)
            )
        
        conn.commit()
        print("Metrics persisted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error persisting metrics: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()
        spark.stop()

if __name__ == "__main__":
    main()
