FROM spark:3.5.8-scala2.12-java17-python3-ubuntu

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    tini \
    procps \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN cd /opt/spark/jars && \
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

COPY requirements.txt /requirements.txt

RUN pip3 install --no-cache-dir -r /requirements.txt

RUN mkdir -p \
    /opt/spark/.ivy2 \
    /opt/spark/.jupyter \
    /opt/spark/conf && \
    chown -R spark:spark /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"
ENV HOME=/opt/spark
ENV JUPYTER_CONFIG_DIR=/opt/spark/.jupyter

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

WORKDIR /opt/spark/work-dir

USER spark

EXPOSE 8888 4040 4041 4042

ENTRYPOINT ["tini", "-g", "--"]

CMD ["bash", "-lc", "FRAME_ANCESTORS=${JUPYTER_FRAME_ANCESTORS:-*}; jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.token=${JUPYTER_TOKEN:-dev-token} --ServerApp.password='' --ServerApp.tornado_settings=\"{\\\"headers\\\":{\\\"Content-Security-Policy\\\":\\\"frame-ancestors ${FRAME_ANCESTORS};\\\",\\\"X-Frame-Options\\\":\\\"ALLOWALL\\\"}}\""]
