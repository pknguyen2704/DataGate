package pknguyen.date_gate;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.HashMap;
import java.util.Map;


public class Load_From_DS_To_Bronze {
    private static final String pgUrl = "";
    private static final String pgUser = "admin";
    private static final String pgPassword = "postgrespassword";
    private static final String pgTable = "yellow_tripdata";
    private static final String pgDriver = "org.postgresql.Driver";

    public static void main(String[] args) {
        // Default
        SparkSession spark = SparkSession.builder()
                .appName("Load_From_DS_To_Bronze")
                .getOrCreate();

        // JdbcOptions
        Map<String, String> jdbcOptions = new HashMap<>();
        jdbcOptions.put("url", pgUrl);
        jdbcOptions.put("dbtable", pgTable);
        jdbcOptions.put("user", pgUser);
        jdbcOptions.put("password", pgPassword);
        jdbcOptions.put("driver", pgDriver);

        Dataset<Row> df = spark.read()
                        .format("jdbc")
                        .options(jdbcOptions)
                        .load();

        df.printSchema();
        df.show(20, false);
        spark.stop();
    }
}