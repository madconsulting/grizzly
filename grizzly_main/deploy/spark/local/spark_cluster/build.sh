#!/bin/bash

# Note: This build command should be run from the root directory of the repo (grizzly/) as follows:
# grizzly_main/deploy/spark/local/spark_cluster/build.sh

# -- Software Stack Version

SPARK_VERSION="3.3.0"
HADOOP_VERSION="3"
POETRY_VERSION="1.2.0b3"
NUMPY_VERSION="1.23.4"

# -- Building the Images

docker build \
  -f grizzly_main/deploy/spark/local/spark_cluster/docker/cluster-base.Dockerfile\
  -t cluster-base .

docker build \
  --build-arg spark_version="${SPARK_VERSION}" \
  --build-arg hadoop_version="${HADOOP_VERSION}" \
  --build-arg numpy_version="${NUMPY_VERSION}" \
  -f grizzly_main/deploy/spark/local/spark_cluster/docker/spark-base.Dockerfile \
  -t spark-base .

docker build \
  -f grizzly_main/deploy/spark/local/spark_cluster/docker/spark-master.Dockerfile \
  -t spark-master .

docker build \
  -f grizzly_main/deploy/spark/local/spark_cluster/docker/spark-worker.Dockerfile \
  -t spark-worker .

docker build \
  --build-arg spark_version="${SPARK_VERSION}" \
  --build-arg poetry_version="${POETRY_VERSION}" \
  -f grizzly_main/deploy/spark/local/spark_cluster/docker/jupyterlab.Dockerfile \
  -t jupyterlab .
