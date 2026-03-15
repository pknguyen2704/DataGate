FROM spark:3.5.7-scala2.12-java17-python3-ubuntu

USER root

RUN apt-get update && \
    apt-get install -y curl wget && \
    rm -rf /var/lib/apt/lists/*

# Custom Spark jars
COPY custom_jars/*.jar /opt/spark/jars/

USER spark