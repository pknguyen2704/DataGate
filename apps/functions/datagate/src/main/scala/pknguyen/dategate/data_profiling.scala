package pknguyen.dategate

import org.apache.spark.sql.SparkSession

object data_profiling {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("[DataGate] Data profiling")
      .getOrCreate()

    println("[DataGate]")

  }
}
