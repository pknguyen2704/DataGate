FROM spark:3.5.7-scala2.12-java17-python3-ubuntu
USER root

RUN cd /opt/spark/jars && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws/1.10.1/iceberg-aws-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.41.34/bundle-2.41.34.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.13-spark-3.5/deequ-2.0.13-spark-3.5.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/fasterxml/jackson/module/jackson-module-scala_2.12/2.21.1/jackson-module-scala_2.12-2.21.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/ch/qos/logback/logback-classic/1.5.32/logback-classic-1.5.32.jar && \
    curl -L -O https://repo1.maven.org/maven2/ch/qos/logback/logback-core/1.5.32/logback-core-1.5.32.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.17/slf4j-api-2.0.17.jar


COPY requirements.txt /opt/spark/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/spark/requirements.txt

USER spark
