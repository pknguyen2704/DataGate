FROM spark:3.5.7-scala2.12-java17-python3-ubuntu
# We removed local COPY custom_jars/*.jar to directly download in the build process
USER root

# Download required JARs directly to /opt/spark/jars
RUN cd /opt/spark/jars && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws/1.10.1/iceberg-aws-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.41.34/bundle-2.41.34.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.13-spark-3.5/deequ-2.0.13-spark-3.5.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/fasterxml/jackson/module/jackson-module-scala_2.12/2.21.1/jackson-module-scala_2.12-2.21.1.jar

COPY requirements.txt /opt/spark/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/spark/requirements.txt

USER spark