FROM bitnami/spark:3.5

USER root

# Install Curl
RUN install_packages curl

# Download Iceberg Spark Runtime
RUN curl -s -L https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.0/iceberg-spark-runtime-3.5_2.12-1.5.0.jar -o /opt/bitnami/spark/jars/iceberg-spark-runtime.jar

# Download AWS Bundle (for S3 support)
# Matching Hadoop 3.3.x which Spark 3.5 uses
RUN curl -s -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -o /opt/bitnami/spark/jars/hadoop-aws.jar
RUN curl -s -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -o /opt/bitnami/spark/jars/aws-java-sdk-bundle.jar

USER 1001
