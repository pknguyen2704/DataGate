package pknguyen.dategate;

import org.apache.spark.sql.SparkSession;

public class data_profiling {
    public static void main (String[] args) throws Exception {
        SparkSession spark = SparkSession.builder()
                .appName("[DataGate] Data profiling")
                .getOrCreate();
        try {
            System.out.println("[INFO] Start data profiling");
        } finally  {
            spark.stop();
        }
    }

}
