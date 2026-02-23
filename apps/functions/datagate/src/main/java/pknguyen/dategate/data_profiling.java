package pknguyen.dategate;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

public class data_profiling {
    public static void main (String[] args) throws Exception {
        SparkSession spark = SparkSession.builder()
                .appName("[DataGate] Data profiling")
                .getOrCreate();
        try {
            System.out.println("[INFO] Start data profiling");
            String table = "rest.bronze.yellow_tripdate";
            Dataset<Row> df = spark.read().format("iceberg").load(table);
            System.out.println(df.count());
        } finally  {
            spark.stop();
        }
    }

}
