package pknguyen.date_gate;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class Load_From_DS_To_Bronze {

    // ----------- Defaults -----------
    private static final String DEFAULT_SOURCE_TABLE = "yellow_tripdata";
    private static final String DEFAULT_TARGET_NAMESPACE = "bronze";
    private static final String DEFAULT_CATALOG = "rest_prod";
    private static final String DEFAULT_REST_URI = "http://iceberg-rest:8181";
    private static final String DEFAULT_WAREHOUSE = "s3://lakehouse/";

    private static final String DEFAULT_PG_HOST = "data_source_postgres";
    private static final String DEFAULT_PG_PORT = "5432";
    private static final String DEFAULT_PG_DB = "postgres";
    private static final String DEFAULT_PG_USER = "admin";
    private static final String DEFAULT_PG_PASS = "postgrespassword";

    private static final String DEFAULT_S3_ENDPOINT = "http://minio:9000";
    private static final String DEFAULT_S3_ACCESS_KEY = "admin";
    private static final String DEFAULT_S3_SECRET_KEY = "miniopassword";
    private static final String DEFAULT_S3_REGION = "us-east-1";

    private static final String MODE_APPEND = "append";
    private static final String MODE_OVERWRITE = "overwrite";

    public static void main(String[] args) {
        Map<String, String> a = parseArgs(args);

        String sourceTable = get(a, "sourceTable", env("SOURCE_TABLE", DEFAULT_SOURCE_TABLE));
        String targetNamespace = get(a, "targetNamespace", env("TARGET_NAMESPACE", DEFAULT_TARGET_NAMESPACE));

        String mode = get(a, "mode", env("MODE", MODE_APPEND)).toLowerCase(Locale.ROOT);
        if (!MODE_APPEND.equals(mode) && !MODE_OVERWRITE.equals(mode)) mode = MODE_APPEND;

        int fetchSize = Integer.parseInt(get(a, "fetchSize", env("JDBC_FETCH_SIZE", "20000")));
        int repartition = Integer.parseInt(get(a, "repartition", env("REPARTITION", "8")));

        // JDBC (env override)
        String pgHost = get(a, "pgHost", env("PG_HOST", DEFAULT_PG_HOST));
        String pgPort = get(a, "pgPort", env("PG_PORT", DEFAULT_PG_PORT));
        String pgDb = get(a, "pgDb", env("PG_DB", DEFAULT_PG_DB));
        String pgUser = get(a, "pgUser", env("PG_USER", DEFAULT_PG_USER));
        String pgPass = get(a, "pgPass", env("PG_PASS", DEFAULT_PG_PASS));

        // Iceberg REST (env override)
        String catalog = get(a, "catalog", env("ICEBERG_CATALOG", DEFAULT_CATALOG));
        String restUri = get(a, "restUri", env("ICEBERG_REST_URI", DEFAULT_REST_URI));
        String warehouse = get(a, "warehouse", env("ICEBERG_WAREHOUSE", DEFAULT_WAREHOUSE));

        // S3/MinIO (env override)
        String s3Endpoint = get(a, "s3Endpoint", env("S3_ENDPOINT", DEFAULT_S3_ENDPOINT));
        String s3AccessKey = get(a, "s3AccessKey", env("S3_ACCESS_KEY", DEFAULT_S3_ACCESS_KEY));
        String s3SecretKey = get(a, "s3SecretKey", env("S3_SECRET_KEY", DEFAULT_S3_SECRET_KEY));
        String s3Region = get(a, "s3Region", env("S3_REGION", DEFAULT_S3_REGION));

        System.out.println("---------------------------------------------");
        System.out.println("Job Config:");
        System.out.println("  Source Table:     " + sourceTable);
        System.out.println("  Target Namespace: " + targetNamespace);
        System.out.println("  Mode:             " + mode);
        System.out.println("  JDBC:             " + pgHost + ":" + pgPort + "/" + pgDb);
        System.out.println("  REST URI:         " + restUri);
        System.out.println("  Warehouse:        " + warehouse);
        System.out.println("  S3 endpoint:      " + s3Endpoint);
        System.out.println("  S3 region:        " + s3Region);
        System.out.println("  fetchSize:        " + fetchSize);
        System.out.println("  repartition:      " + repartition);
        System.out.println("---------------------------------------------");

        SparkSession spark = createSparkSession(catalog, restUri, warehouse, s3Endpoint, s3AccessKey, s3SecretKey, s3Region);

        try {
            // 1) Ensure namespace exists
            spark.sql("CREATE NAMESPACE IF NOT EXISTS " + catalog + "." + targetNamespace);

            // 2) Read from Postgres
            String jdbcUrl = String.format("jdbc:postgresql://%s:%s/%s", pgHost, pgPort, pgDb);

            Dataset<Row> df = spark.read()
                    .format("jdbc")
                    .option("url", jdbcUrl)
                    .option("dbtable", sourceTable)
                    .option("user", pgUser)
                    .option("password", pgPass)
                    .option("driver", "org.postgresql.Driver")
                    .option("fetchsize", String.valueOf(fetchSize))
                    .load();

            df = normalizeColumnsToLower(df);

            if (repartition > 0) df = df.repartition(repartition);

            // 3) Write to Iceberg
            String fullTableName = catalog + "." + targetNamespace + "." + sourceTable;
            System.out.println("Target Iceberg table: " + fullTableName);

            boolean exists = spark.catalog().tableExists(fullTableName);

            if (MODE_OVERWRITE.equals(mode)) {
                System.out.println("Writing overwrite...");
                // overwrite should create if not exists
                df.writeTo(fullTableName).createOrReplace();
            } else {
                System.out.println("Writing append...");
                if (!exists) {
                    System.out.println("Table not found -> createOrReplace first");
                    df.writeTo(fullTableName).createOrReplace();
                } else {
                    df.writeTo(fullTableName).append();
                }
            }

            System.out.println("✅ SUCCESS: wrote data to " + fullTableName);

        } catch (Exception e) {
            System.err.println("❌ FAILED: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException(e);
        } finally {
            spark.stop();
        }
    }

    private static SparkSession createSparkSession(
            String catalog, String restUri, String warehouse,
            String s3Endpoint, String s3AccessKey, String s3SecretKey, String s3Region
    ) {
        // Make region resolvable in driver JVM (still recommend executorEnv in spark-submit too)
        System.setProperty("aws.region", s3Region);
        System.setProperty("aws.default.region", s3Region);

        return SparkSession.builder()
                .appName("DataGate - Load DS to Bronze")
                .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
                .config("spark.sql.defaultCatalog", catalog)

                .config("spark.sql.catalog." + catalog, "org.apache.iceberg.spark.SparkCatalog")
                .config("spark.sql.catalog." + catalog + ".type", "rest")
                .config("spark.sql.catalog." + catalog + ".uri", restUri)

                .config("spark.sql.catalog." + catalog + ".warehouse", warehouse)
                .config("spark.sql.catalog." + catalog + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

                .config("spark.sql.catalog." + catalog + ".s3.endpoint", s3Endpoint)
                .config("spark.sql.catalog." + catalog + ".s3.path-style-access", "true")
                .config("spark.sql.catalog." + catalog + ".s3.access-key-id", s3AccessKey)
                .config("spark.sql.catalog." + catalog + ".s3.secret-access-key", s3SecretKey)
                .config("spark.sql.catalog." + catalog + ".s3.ssl.enabled", "false")
                .config("spark.sql.catalog." + catalog + ".s3.region", s3Region)

                .getOrCreate();
    }

    private static Dataset<Row> normalizeColumnsToLower(Dataset<Row> df) {
        for (String c : df.columns()) {
            String lower = c.toLowerCase(Locale.ROOT);
            if (!c.equals(lower)) df = df.withColumnRenamed(c, lower);
        }
        return df;
    }

    private static String env(String k, String def) {
        String v = System.getenv(k);
        return (v == null || v.isBlank()) ? def : v;
    }

    private static String get(Map<String, String> args, String key, String def) {
        String v = args.get(key);
        return (v == null || v.isBlank()) ? def : v;
    }

    private static Map<String, String> parseArgs(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            String a = args[i];
            if (a.startsWith("--")) {
                String key = a.substring(2);
                String val = (i + 1 < args.length && !args[i + 1].startsWith("--")) ? args[++i] : "true";
                m.put(key, val);
            }
        }
        return m;
    }
}