FROM apache/airflow:2.11.2-python3.10

USER root

# Cài đặt system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk \
        curl \
        ca-certificates \
        tar \
        libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cấu hình Java
RUN mkdir -p /opt/java \
    && ln -s /usr/lib/jvm/java-17-openjdk-amd64 /opt/java/openjdk

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Cài đặt Spark
RUN curl -fL https://downloads.apache.org/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz -o /tmp/spark.tgz \
    && tar -xzf /tmp/spark.tgz -C /opt/ \
    && mv /opt/spark-3.5.8-bin-hadoop3 /opt/spark \
    && rm -f /tmp/spark.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

# Cài đặt Spark jars
RUN mkdir -p /opt/spark/jars && \
    cd /opt/spark/jars && \
    curl -L -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar && \
    curl -L -O https://repo1.maven.org/maven2/io/trino/trino-jdbc/480/trino-jdbc-480.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.42.39/bundle-2.42.39.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.16-spark-3.5/deequ-2.0.16-spark-3.5.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/azure/synapseml_2.12/1.1.3/synapseml_2.12-1.1.3.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/azure/synapseml-core_2.12/1.1.3/synapseml-core_2.12-1.1.3.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/azure/synapseml-lightgbm_2.12/1.1.3/synapseml-lightgbm_2.12-1.1.3.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/ml/lightgbm/lightgbmlib/3.3.510/lightgbmlib-3.3.510.jar && \
    curl -L -O https://repo1.maven.org/maven2/io/spray/spray-json_2.12/1.3.5/spray-json_2.12-1.3.5.jar

# Cấp quyền cho user airflow
RUN chown -R airflow:root /opt/spark

# Cài đặt Python dependencies
COPY requirements.txt /requirements.txt

USER airflow

RUN pip install --no-cache-dir -r /requirements.txt

USER root

# Copy source code DataGate
RUN mkdir -p /opt/datagate

COPY datagate /opt/datagate

RUN chown -R airflow:root /opt/datagate

USER airflow

ENV DATAGATE_HOME=/opt/datagate
ENV PYTHONPATH="/opt:${DATAGATE_HOME}"
