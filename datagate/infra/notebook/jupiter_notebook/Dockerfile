FROM spark:3.5.8-scala2.12-java17-python3-ubuntu

USER root

# Cài thêm tool cần cho notebook container
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    tini \
    procps \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Đồng bộ JAR với Spark cluster hiện tại
RUN cd /opt/spark/jars && \
    curl -L -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar && \
    curl -L -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar && \
    curl -L -O https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.42.39/bundle-2.42.39.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/amazon/deequ/deequ/2.0.16-spark-3.5/deequ-2.0.16-spark-3.5.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/azure/synapseml_2.12/1.1.3/synapseml_2.12-1.1.3.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/azure/synapseml-core_2.12/1.1.3/synapseml-core_2.12-1.1.3.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/azure/synapseml-lightgbm_2.12/1.1.3/synapseml-lightgbm_2.12-1.1.3.jar && \
    curl -L -O https://repo1.maven.org/maven2/com/microsoft/ml/lightgbm/lightgbmlib/3.3.510/lightgbmlib-3.3.510.jar && \
    curl -L -O https://repo1.maven.org/maven2/io/spray/spray-json_2.12/1.3.5/spray-json_2.12-1.3.5.jar
# Cài Python packages dùng chung cho Spark + notebook
COPY requirements.txt /opt/spark/requirements.txt

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r /opt/spark/requirements.txt

# Tạo thư mục làm việc cho notebook
RUN mkdir -p \
    /opt/spark/notebooks \
    /opt/spark/workspace \
    /opt/spark/.ivy2 \
    /opt/spark/.jupyter \
    /opt/spark/conf && \
    chown -R spark:spark /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

WORKDIR /opt/spark/notebooks

USER spark

EXPOSE 8888 4040 4041 4042

ENTRYPOINT ["tini", "-g", "--"]

CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.token=${JUPYTER_TOKEN:-dev-token} --ServerApp.password=''"]