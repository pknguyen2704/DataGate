FROM apache/spark:3.5.8-scala2.12-java17-python3-r-ubuntu

COPY custom_jars/*.jar /opt/spark/jars/
USER root
RUN pip3 install prometheus_client

USER spark