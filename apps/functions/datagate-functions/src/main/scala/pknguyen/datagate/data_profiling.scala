package pknguyen.datagate

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._

object data_profiling {

  def main(args: Array[String]): Unit = {

    val JOB_NAME = "[DataGate] Data Profiling"
    val CATALOG = "rest"
    val NAMESPACE = "bronze"
    val TABLE = "yellow_tripdata"

    val spark = SparkSession.builder()
      .appName(JOB_NAME)
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.rest", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.rest.type", "rest")
      .config("spark.sql.catalog.rest.uri", "http://iceberg-rest:8181")
      .config("spark.sql.catalog.rest.warehouse", "s3://lakehouse/")
      .config("spark.sql.catalog.rest.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
      .config("spark.sql.catalog.rest.s3.endpoint", "http://minio:9000")
      .config("spark.sql.catalog.rest.s3.path-style-access", "true")
      .config("spark.sql.catalog.rest.s3.access-key-id", "admin")
      .config("spark.sql.catalog.rest.s3.secret-access-key", "miniopassword")
      .config("spark.sql.catalog.rest.s3.region", "us-east-1")
      .config("spark.sql.catalog.rest.s3.ssl-enabled", "false")
      .config("spark.sql.shuffle.partitions", "8")
      .getOrCreate()

    try {

      // 🔥 Nếu muốn incremental theo partition:
      // val df = spark.table(s"$CATALOG.$NAMESPACE.$TABLE")
      //   .where("date_hour >= '2026-02-28-00'")

      val df = spark.table(s"$CATALOG.$NAMESPACE.$TABLE")

      val totalCount = df.count()

      println(s"Total rows: $totalCount")

      val aggExprs = df.columns.flatMap { colName =>
        Seq(
          count(col(colName)).alias(s"${colName}__non_null"),
          approx_count_distinct(col(colName)).alias(s"${colName}__distinct")
        )
      }

      val resultRow = df.agg(aggExprs.head, aggExprs.tail: _*).collect()(0)

      df.columns.foreach { colName =>

        val nonNull = resultRow.getAs[Long](s"${colName}__non_null")
        val distinct = resultRow.getAs[Long](s"${colName}__distinct")

        val completeness = nonNull.toDouble / totalCount.toDouble
        val dataType = df.schema(colName).dataType.typeName

        println(
          s"""
Column: $colName
  completeness: $completeness
  approx distinct: $distinct
  datatype: $dataType
"""
        )
      }

    } finally {
      spark.stop()
    }
  }
}