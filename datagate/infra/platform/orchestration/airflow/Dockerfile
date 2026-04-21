FROM apache/airflow:2.11.2

USER root

# Cài đặt Java 17
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && mkdir -p /opt/java \
    && curl -L https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.10%2B7/OpenJDK17U-jdk_aarch64_linux_hotspot_17.0.10_7.tar.gz | tar -xz -C /opt/java \
    && mv /opt/java/jdk-17.0.10+7 /opt/java/openjdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

RUN curl -L https://downloads.apache.org/spark/spark-3.5.7/spark-3.5.7-bin-hadoop3.tgz \
    | tar -xz -C /opt/ \
    && ln -s /opt/spark-3.5.7-bin-hadoop3 /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

# Tải các JAR vào /opt/spark/jars (Đường dẫn chuẩn cho Airflow worker)
RUN mkdir -p /opt/spark/jars && cd /opt/spark/jars && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws/1.10.1/iceberg-aws-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.42.35/bundle-2.42.35.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.16-spark-3.5/deequ-2.0.16-spark-3.5.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/fasterxml/jackson/module/jackson-module-scala_2.12/2.21.1/jackson-module-scala_2.12-2.21.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/ch/qos/logback/logback-classic/1.5.32/logback-classic-1.5.32.jar && \
    curl -L -O https://repo1.maven.org/maven2/ch/qos/logback/logback-core/1.5.32/logback-core-1.5.32.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.17/slf4j-api-2.0.17.jar

# Cấp quyền cho user airflow (group root là mặc định trong image Airflow)
RUN chown -R airflow:root /opt/spark/jars

# Cài đặt các phụ thuộc Python từ requirements.txt
COPY requirements.txt /requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /requirements.txt