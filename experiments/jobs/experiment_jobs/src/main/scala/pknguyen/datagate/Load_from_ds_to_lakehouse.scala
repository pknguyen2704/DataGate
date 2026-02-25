package pknguyen.datagate

import org.apache.spark.sql.SparkSession

object Load_from_ds_to_lakehouse {
  def main(args: Array[String]): Unit = {
    val JOB_NAME = "[Experiment jobs] Load From DS to Lakehouse"

    val spark = SparkSession.builder().appName(JOB_NAME).getOrCreate()

    try {
      val a = 10
      val b = 11
      println(s"[result] ${a + b}")
    } finally {
      spark.stop()
    }
  }
}
