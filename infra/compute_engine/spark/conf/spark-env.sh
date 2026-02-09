#!/usr/bin/env bash

# This file is sourced when running various Spark programs.
# It is used to set environment variables for the Spark daemons (Master/Worker).

SPARK_MASTER_OPTS="-Dspark.ui.prometheus.enabled=true -Duser.timezone=Asia/Ho_Chi_Minh"
SPARK_WORKER_OPTS="-Dspark.ui.prometheus.enabled=true -Duser.timezone=Asia/Ho_Chi_Minh"
