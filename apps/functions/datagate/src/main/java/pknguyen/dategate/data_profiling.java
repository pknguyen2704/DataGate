package pknguyen.dategate;

import org.apache.spark.sql.SparkSession;

public class data_profiling {
    public static void main(String[] args) throws Exception{
        long jobStart = System.currentTimeMillis();
        SparkSession spark = SparkSession.builder()
                .appName("[DataGate] Data profiling")
                .getOrCreate();
        try {
            System.out.println("[DataGate] Data profiling function start");
        } finally {
            spark.stop();
        }
        System.out.println("DataGate Data Profiling job");
    }
}
