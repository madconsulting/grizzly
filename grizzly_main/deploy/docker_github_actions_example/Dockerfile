FROM python:3.9.12

ENV APP_NAME="hello_world_app"

# Set the working directory in the container
WORKDIR /$APP_NAME

# Copy the Poetry files and the grizzly_main package folder to the container
COPY pyproject.toml poetry.lock ./
COPY grizzly_main/ grizzly_main/

# Install Poetry and project dependencies
RUN pip install poetry
RUN poetry install

# The ENTRYPOINT is set to an empty command, which means that there's no default
# command executed when the container starts. This allows you to override the command
# when running the container.
ENTRYPOINT []

# The CMD instruction is set to run /bin/bash, which gives us an interactive shell
# inside the container by default.
CMD ["/bin/bash"]
