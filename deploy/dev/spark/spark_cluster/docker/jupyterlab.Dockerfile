FROM cluster-base

ARG spark_version
ARG poetry_version

WORKDIR ${SHARED_WORKSPACE}

# Install Poetry environment, including the spark_cluster package files
# IMPORTANT NOTE: The docker docker command is expected to be run from the root path of the repository
# Copy poetry files: pyproject.toml and poetry.lock into our working directory
COPY pyproject.toml poetry.lock ./
# Copy the spark_cluster folder, which package will be installed in poetry:
COPY spark_cluster/ spark_cluster/
# Create a virtual environment & make Poetry packages to be installed to this venv
RUN apt-get update -y && apt-get install -y python3-pip python3-venv
RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install poetry==${poetry_version}
ENV PATH="$PATH:/root/.poetry/bin:/root/.local/bin"
ENV VIRTUAL_ENV="/venv"
ENV PATH="$PATH:/$VIRTUAL_ENV/bin"
RUN python -m venv $VIRTUAL_ENV
RUN poetry install

# -- Runtime
EXPOSE 8888
# This command will be executed from the venv
CMD jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=