package pknguyen.date_gate;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.Properties;

public class Load_From_DS_To_Bronze {

    public static void main(String[] args) {
        // Default Configuration
        String sourceTable = "yellow_tripdata";
        String targetNamespace = "bronze";

        String pgHost = "data_source_postgres";
        String pgPort = "5432";
        String pgDb = "postgres";
        String pgUser = "admin";
        String pgPass = "postgrespassword";

        // MinIO (S3-compatible)
        String s3Endpoint = "http://minio:9000";
        String s3AccessKey = "admin";
        String s3SecretKey = "miniopassword";

        // Override with arguments if provided
        // Usage: java ... <sourceTable> <targetNamespace> <pgHost> <pgPort> <pgDb>
        // <pgUser> <pgPass> <s3Endpoint> <s3AccessKey> <s3SecretKey>
        if (args.length >= 1) sourceTable = args[0];
        if (args.length >= 2) targetNamespace = args[1];
        if (args.length >= 3) pgHost = args[2];
        if (args.length >= 4) pgPort = args[3];
        if (args.length >= 5) pgDb = args[4];
        if (args.length >= 6) pgUser = args[5];
        if (args.length >= 7) pgPass = args[6];
        if (args.length >= 8) s3Endpoint = args[7];
        if (args.length >= 9) s3AccessKey = args[8];
        if (args.length >= 10) s3SecretKey = args[9];

        System.out.println("---------------------------------------------");
        System.out.println("Job Config:");
        System.out.println("  Source Table: " + sourceTable);
        System.out.println("  Target Namespace: " + targetNamespace);
        System.out.println("  Postgres: " + pgHost + ":" + pgPort + "/" + pgDb);
        System.out.println("  MinIO Endpoint: " + s3Endpoint);
        System.out.println("---------------------------------------------");

        SparkSession spark = createSparkSession(s3Endpoint, s3AccessKey, s3SecretKey);

        // Postgres Connection
        String jdbcUrl = String.format("jdbc:postgresql://%s:%s/%s", pgHost, pgPort, pgDb);
        Properties connectionProperties = new Properties();
        connectionProperties.put("user", pgUser);
        connectionProperties.put("password", pgPass);
        connectionProperties.put("driver", "org.postgresql.Driver");
        connectionProperties.put("fetchsize", "5000");

        try {
            System.out.println("Reading data from Postgres table: " + sourceTable);
            Dataset<Row> jdbcDF = spark.read().jdbc(jdbcUrl, sourceTable, connectionProperties);

            System.out.println("Source Schema:");
            jdbcDF.printSchema();

            String catalogName = "rest_prod";
            String tableName = sourceTable;
            String fullTableName = catalogName + "." + targetNamespace + "." + tableName;

            System.out.println("Target Iceberg table: " + fullTableName);

            createNamespaceIfNotExists(spark, catalogName, targetNamespace);

            System.out.println("Writing data to Bronze layer...");
            jdbcDF.writeTo(fullTableName).createOrReplace();

            System.out.println("Successfully wrote data to " + fullTableName);

        } catch (Exception e) {
            System.err.println("Error processing data: " + e.getMessage());
            e.printStackTrace();
        } finally {
            spark.stop();
        }
    }

    /**
     * SDK v2 path: Iceberg S3FileIO + s3://
     * IMPORTANT: This requires Iceberg AWS bundle (or equivalent AWS SDK v2 deps) on Spark classpath.
     */
    private static SparkSession createSparkSession(String s3Endpoint, String s3AccessKey, String s3SecretKey) {
        return SparkSession.builder()
                .appName("DataGate - Load DS to Bronze")

                // Iceberg extensions
                .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

                // (Optional but nice) default catalog
                .config("spark.sql.defaultCatalog", "rest_prod")

                // REST catalog
                .config("spark.sql.catalog.rest_prod", "org.apache.iceberg.spark.SparkCatalog")
                .config("spark.sql.catalog.rest_prod.type", "rest")
                .config("spark.sql.catalog.rest_prod.uri", "http://iceberg-rest:8181")

                // IMPORTANT: use s3:// (not s3a://) when using S3FileIO (SDK v2)
                .config("spark.sql.catalog.rest_prod.warehouse", "s3://lakehouse/")

                // Force Iceberg to use AWS SDK v2 S3FileIO
                .config("spark.sql.catalog.rest_prod.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

                // MinIO / S3FileIO settings (Iceberg properties, not Hadoop fs.s3a)
                .config("spark.sql.catalog.rest_prod.s3.endpoint", s3Endpoint)
                .config("spark.sql.catalog.rest_prod.s3.path-style-access", "true")
                .config("spark.sql.catalog.rest_prod.s3.access-key-id", s3AccessKey)
                .config("spark.sql.catalog.rest_prod.s3.secret-access-key", s3SecretKey)
                .config("spark.sql.catalog.rest_prod.s3.ssl.enabled", "false")
                .config("spark.sql.catalog.rest_prod.s3.region", "us-east-1")

                .getOrCreate();
    }

    private static void createNamespaceIfNotExists(SparkSession spark, String catalog, String namespace) {
        try {
            spark.sql("CREATE NAMESPACE IF NOT EXISTS " + catalog + "." + namespace);
            System.out.println("Namespace " + namespace + " checked/created.");
        } catch (Exception nsEx) {
            System.out.println("Warning: Could not create namespace: " + nsEx.getMessage());
        }
    }
}