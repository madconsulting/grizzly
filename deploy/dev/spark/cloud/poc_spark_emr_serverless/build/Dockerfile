FROM --platform=linux/amd64 amazonlinux:2 AS base

ARG PYTHON_VERSION
ARG PYTHON_VERSION_SHORT
ARG POETRY_VERSION

# Install Python - Note that python 3.10 requires OpenSSL >= 1.1.1 (installing it by default)
RUN yum install -y gcc openssl11-devel bzip2-devel libffi-devel tar gzip wget make && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make install

# Install Poetry and then convert the .lock file into a requirements.txt file
# Copy poetry files: pyproject.toml and poetry.lock into our working directory
COPY pyproject.toml poetry.lock ./
# Copy the deploy folder (containing the poetry package and the local/spark_cluster folder):
COPY deploy/ deploy/
# Install Poetry environment
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade setuptools && \
    python3 -m pip install poetry==${POETRY_VERSION}
RUN poetry install --no-root
RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN poetry build --format wheel

# Create our virtual environment
# we need both --copies for python executables for cp for libraries
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV --copies
# Install requirements previously exported via Poetry:
RUN pip install -r requirements.txt
RUN cp -r /usr/local/lib/python${PYTHON_VERSION_SHORT}/* $VIRTUAL_ENV/lib/python${PYTHON_VERSION_SHORT}/

# Ensure our python3 executable references the virtual environment
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Package the env
# note you have to supply --python-prefix option to make sure python starts with the path where your copied libraries are present
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install venv-pack==0.2.0
RUN mkdir /output && \
    venv-pack -f -o /output/pyspark_${PYTHON_VERSION}.tar.gz --python-prefix /home/hadoop/environment

FROM scratch AS export
ARG PYTHON_VERSION
COPY --from=base output/pyspark_${PYTHON_VERSION}.tar.gz deploy/dev/spark/cloud/poc_spark_emr_serverless/build/artifacts/venvs/
COPY --from=base dist/ deploy/dev/spark/cloud/poc_spark_emr_serverless/build/artifacts/package_wheel_files/