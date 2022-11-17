FROM cluster-base

ARG spark_version
ARG hadoop_version
ARG numpy_version

# Apache Spark
RUN apt-get update -y && \
    apt-get install -y curl && \
    curl https://archive.apache.org/dist/spark/spark-${spark_version}/spark-${spark_version}-bin-hadoop${hadoop_version}.tgz -o spark.tgz && \
    tar -xf spark.tgz && \
    mv spark-${spark_version}-bin-hadoop${hadoop_version} /usr/bin/ && \
    mkdir /usr/bin/spark-${spark_version}-bin-hadoop${hadoop_version}/logs && \
    rm spark.tgz
ENV SPARK_HOME /usr/bin/spark-${spark_version}-bin-hadoop${hadoop_version}
ENV SPARK_MASTER_HOST spark-master
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3

# Numpy - required in all the spark nodes for jobs which include pyspark.mllib imports. Note: It had to be installed
# with pip as root, instead of poetry, in order accessible at runtime by spark
RUN apt-get update -y && apt-get install -y python3-pip
RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install numpy==${numpy_version}

# -- Runtime
WORKDIR ${SPARK_HOME}
