package pknguyen.dategate

import org.apache.spark.sql.SparkSession

object data_profiling {
    def main(args: Array[String]): Unit = {
        println("[DataGate] Data Profiling...")
        
        val spark = SparkSession.builder()
            .appName("[DataGate] Data Profiling")
            .config()
            .getOrCreate()
        
        spark.stop()
    }
}