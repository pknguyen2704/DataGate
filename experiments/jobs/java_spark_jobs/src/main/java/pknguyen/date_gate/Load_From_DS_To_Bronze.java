package pknguyen.date_gate;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.HashMap;
import java.util.Map;

public class Load_From_DS_To_Bronze {

    // ===== Postgres =====
    private static final String PG_URL = "jdbc:postgresql://data_source_postgres:5432/postgres";
    private static final String PG_USER = "admin";
    private static final String PG_PASSWORD = "postgrespassword";
    private static final String PG_TABLE = "yellow_tripdata";
    private static final String PG_DRIVER = "org.postgresql.Driver";

    // ===== Iceberg REST Catalog =====
    private static final String CATALOG = "rest";
    private static final String NAMESPACE = "bronze";
    private static final String ICEBERG_TABLE = "yellow_tripdata";
    private static final String REST_URI = "http://iceberg-rest:8181";
    private static final String WAREHOUSE = "s3://lakehouse/";

    // ===== MinIO (S3 compatible) =====
    private static final String S3_ENDPOINT = "http://minio:9000";
    private static final String S3_ACCESS_KEY = "admin";
    private static final String S3_SECRET_KEY = "miniopassword";
    private static final String AWS_REGION = "us-east-1";

    // ===== Performance knobs (tune these) =====
    private static final int JDBC_NUM_PARTITIONS = 8;      // ~ 2x total cores (you have 4 cores total)
    private static final int JDBC_FETCH_SIZE = 10000;      // reduce JDBC round-trips
    private static final int OUTPUT_FILES = 4;             // number of output files (coalesce) for small/medium loads

    // Pick a numeric column with decent distribution.
    // If vendorid has only a few values, switch to a better column (e.g., an integer primary key).
    private static final String JDBC_PARTITION_COLUMN = "vendorid";

    public static void main(String[] args) throws Exception {
        long jobStart = System.currentTimeMillis();

        SparkSession spark = SparkSession.builder()
                .appName("Load_From_DS_To_Bronze_Optimized")
                .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

                // Catalog REST
                .config("spark.sql.catalog." + CATALOG, "org.apache.iceberg.spark.SparkCatalog")
                .config("spark.sql.catalog." + CATALOG + ".type", "rest")
                .config("spark.sql.catalog." + CATALOG + ".uri", REST_URI)
                .config("spark.sql.catalog." + CATALOG + ".warehouse", WAREHOUSE)

                // Iceberg S3FileIO
                .config("spark.sql.catalog." + CATALOG + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

                // Iceberg S3 settings (MinIO)
                .config("spark.sql.catalog." + CATALOG + ".s3.endpoint", S3_ENDPOINT)
                .config("spark.sql.catalog." + CATALOG + ".s3.path-style-access", "true")
                .config("spark.sql.catalog." + CATALOG + ".s3.access-key-id", S3_ACCESS_KEY)
                .config("spark.sql.catalog." + CATALOG + ".s3.secret-access-key", S3_SECRET_KEY)
                .config("spark.sql.catalog." + CATALOG + ".s3.region", AWS_REGION)
                .config("spark.sql.catalog." + CATALOG + ".client.region", AWS_REGION)
                .config("spark.sql.catalog." + CATALOG + ".s3.ssl-enabled", "false")

                // MinIO/S3 perf (usually helps when many small files/requests)
                .config("spark.sql.catalog." + CATALOG + ".s3.connection.maximum", "200")

                // This job (load+append) typically doesn't need big shuffle
                .config("spark.sql.shuffle.partitions", "8")

                .getOrCreate();

        try {
            String fullTableName = CATALOG + "." + NAMESPACE + "." + ICEBERG_TABLE;

            // 1) Ensure namespace
            spark.sql("CREATE NAMESPACE IF NOT EXISTS " + CATALOG + "." + NAMESPACE);

            // 2) Get min/max for partition bounds (cheap query)
            long boundsStart = System.currentTimeMillis();
            Map<String, String> boundsOptions = new HashMap<>();
            boundsOptions.put("url", PG_URL);
            boundsOptions.put("dbtable",
                    "(SELECT MIN(" + JDBC_PARTITION_COLUMN + ") AS minv, " +
                            "MAX(" + JDBC_PARTITION_COLUMN + ") AS maxv " +
                            "FROM " + PG_TABLE + ") AS t");
            boundsOptions.put("user", PG_USER);
            boundsOptions.put("password", PG_PASSWORD);
            boundsOptions.put("driver", PG_DRIVER);
            boundsOptions.put("fetchsize", "1");

            Row bounds = spark.read().format("jdbc").options(boundsOptions).load().first();
            long boundsEnd = System.currentTimeMillis();

            if (bounds == null || bounds.isNullAt(0) || bounds.isNullAt(1)) {
                throw new IllegalStateException("Cannot compute bounds for partitioning. " +
                        "Column '" + JDBC_PARTITION_COLUMN + "' may be NULL or table empty.");
            }

            long lowerBound = ((Number) bounds.get(0)).longValue();
            long upperBound = ((Number) bounds.get(1)).longValue();

            // If all values same, fallback to single partition to avoid JDBC partition errors
            boolean canPartition = upperBound > lowerBound;

            // 3) Read data from Postgres (parallel if possible)
            Map<String, String> jdbcOptions = new HashMap<>();
            jdbcOptions.put("url", PG_URL);
            jdbcOptions.put("dbtable", PG_TABLE);
            jdbcOptions.put("user", PG_USER);
            jdbcOptions.put("password", PG_PASSWORD);
            jdbcOptions.put("driver", PG_DRIVER);
            jdbcOptions.put("fetchsize", String.valueOf(JDBC_FETCH_SIZE));

            if (canPartition) {
                jdbcOptions.put("partitionColumn", JDBC_PARTITION_COLUMN);
                jdbcOptions.put("lowerBound", String.valueOf(lowerBound));
                jdbcOptions.put("upperBound", String.valueOf(upperBound));
                jdbcOptions.put("numPartitions", String.valueOf(JDBC_NUM_PARTITIONS));
            }

            long readStart = System.currentTimeMillis();
            Dataset<Row> df = spark.read()
                    .format("jdbc")
                    .options(jdbcOptions)
                    .load();
            long readEnd = System.currentTimeMillis();

            // 4) Create table only once (no CTAS WHERE 1=0; no show/count/cache)
            boolean tableExists = spark.catalog().tableExists(fullTableName);

            // Optional: control number of output files for small/medium loads
            Dataset<Row> outDf = df.coalesce(OUTPUT_FILES);

            long writeStart = System.currentTimeMillis();
            if (!tableExists) {
                // create schema from dataframe
                outDf.writeTo(fullTableName).create();
            } else {
                outDf.writeTo(fullTableName).append();
            }
            long writeEnd = System.currentTimeMillis();

            long jobEnd = System.currentTimeMillis();

            System.out.println("✅ Iceberg table: " + fullTableName);
            System.out.println("✅ JDBC partitioning: " + (canPartition ? "ON" : "OFF")
                    + " (" + JDBC_PARTITION_COLUMN + ", " + lowerBound + " -> " + upperBound + ")");
            System.out.println("✅ JDBC fetchsize: " + JDBC_FETCH_SIZE);
            System.out.println("✅ Output files (coalesce): " + OUTPUT_FILES);

            System.out.println("⏱ Job time: " + (jobEnd - jobStart) + " ms");
            System.out.println("⏱ Bounds query time: " + (boundsEnd - boundsStart) + " ms");
            System.out.println("⏱ Read time: " + (readEnd - readStart) + " ms");
            System.out.println("⏱ Write time: " + (writeEnd - writeStart) + " ms");

        } finally {
            spark.stop();
        }
    }
}