FROM spark:3.5.8-scala2.12-java17-python3-ubuntu

USER root

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

COPY requirements.txt /opt/spark/requirements.txt

RUN pip3 install --no-cache-dir -r /opt/spark/requirements.txt

USER spark