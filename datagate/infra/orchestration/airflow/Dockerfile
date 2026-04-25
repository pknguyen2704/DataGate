FROM apache/airflow:2.11.2

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk \
        curl \
        ca-certificates \
        tar \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

RUN curl -fL https://downloads.apache.org/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz -o /tmp/spark.tgz \
    && tar -xzf /tmp/spark.tgz -C /opt/ \
    && ln -s /opt/spark-3.5.8-bin-hadoop3 /opt/spark \
    && rm /tmp/spark.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

RUN mkdir -p /opt/spark/jars && cd /opt/spark/jars && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.13/1.10.1/iceberg-spark-runtime-3.5_2.13-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.42.39/bundle-2.42.39.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.16-spark-3.5/deequ-2.0.16-spark-3.5.jar

# Cấp quyền cho user airflow (group root là mặc định trong image Airflow)
RUN chown -R airflow:root /opt/spark/jars

# Cài đặt các phụ thuộc Python từ requirements.txt
COPY requirements.txt /requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /requirements.txt