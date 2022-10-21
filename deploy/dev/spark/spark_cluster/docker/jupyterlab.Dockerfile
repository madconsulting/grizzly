FROM cluster-base

# -- Layer: JupyterLab + Poetry

ARG spark_version
ARG jupyterlab_version

WORKDIR ${SHARED_WORKSPACE}

# IMPORTANT NOTE: The docker docker command is expected to be run from the root path of the repository
# Copy poetry files: pyproject.toml and poetry.lock into our working directory
COPY pyproject.toml poetry.lock ./
# Copy the spark_cluster folder, which package will be installed in poetry:
COPY spark_cluster/ spark_cluster/

# Create a virtual environment & make Poetry packages to be installed to this venv
RUN apt-get update -y && apt-get install -y curl python3-pip python3-venv
RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install poetry==1.2.0b3
ENV PATH="$PATH:/root/.poetry/bin:/root/.local/bin"
ENV VIRTUAL_ENV="/venv"
ENV PATH="$PATH:/$VIRTUAL_ENV/bin"
RUN python -m venv $VIRTUAL_ENV
RUN poetry install

# Debug folder
RUN echo $(ls)

# -- Runtime

EXPOSE 8888
# This command will be executed from the venv
CMD jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=