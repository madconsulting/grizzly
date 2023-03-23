# --  Print inputs
echo "Inputs to deploy Spark cloud env to s3:"
echo "PYTHON_VERSION=$PYTHON_VERSION"
echo "PYTHON_VERSION_SHORT=$PYTHON_VERSION_SHORT"
echo "POETRY_VERSION=$POETRY_VERSION"
echo "POETRY_DIR=$POETRY_DIR"
echo "GRIZZLY_BASE_DIR=$GRIZZLY_BASE_DIR"
echo "CLIENT_REPO_BASE_DIR=$CLIENT_REPO_BASE_DIR"
echo "S3_BUCKET=$S3_BUCKET"

# -- Build the custom venv and package wheel files from Poetry in Docker (with BuildKit backend)
echo "Building the custom venv and package wheel files from Poetry in Docker (with BuildKit backend)"
# NOTE: Remove the quiet flag (-q) for debugging purposes
# NOTE 2: The build of the docker will work only when it is executed from a client repo and passing the correct
# poetry directory (as the base directory from where we execute the dockerfile needs to be grizzly_base/, because the
# child directory will only contain the grizzly_base package, but not the files in the previous directory, grizzly/)
DOCKER_BUILDKIT=1 docker build \
  --build-arg PYTHON_VERSION="$PYTHON_VERSION" \
  --build-arg PYTHON_VERSION_SHORT="$PYTHON_VERSION_SHORT" \
  --build-arg POETRY_VERSION="$POETRY_VERSION" \
  --build-arg GRIZZLY_BASE_DIR="$GRIZZLY_BASE_DIR" \
  --build-arg CLIENT_REPO_BASE_DIR="$CLIENT_REPO_BASE_DIR" \
  -f "$GRIZZLY_BASE_DIR/deploy/spark/cloud/spark_emr_serverless/build/Dockerfile" \
  -o "$GRIZZLY_BASE_DIR" . # current directory (.) as build context + export output files to $GRIZZLY_BASE_DIR
# TODO - ensure that docker build stops and raises error in -q mode, for now we have disabled quiet mode, to prevent that

# -- Upload the virtual environment to S3
echo "Adding Poetry package version to venv file name"
script="$GRIZZLY_BASE_DIR/deploy/spark/cloud/spark_emr_serverless/build/build_artifacts_interactions.py"
function="add_package_version_to_venv"
python_run_command="poetry run python3 $script $function $POETRY_DIR $CLIENT_REPO_BASE_DIR"
echo "Python command to add the package version to the venv file name: $python_run_command"
# Reading output from STDOUT
venv_file_path=$($python_run_command)
echo "Venv file: $venv_file_path"
echo "Uploading the virtual environment to S3"
aws s3 mv "$venv_file_path" "s3://$S3_BUCKET/artifacts/venvs/"

# -- Upload the wheel file to S3
echo "Retrieving Poetry wheel file already generated by Poetry in Docker"
function="rename_poetry_wheel_file"
python_run_command="poetry run python3 $script $function $POETRY_DIR $CLIENT_REPO_BASE_DIR"
echo "Python command to rename the wheel file: $python_run_command"
# Reading output from STDOUT
wheel_file_path=$($python_run_command)
echo "Wheel file: $wheel_file_path"
echo "Uploading the wheel file to S3"
# Note that we move the file and we don't keep a file locally, to prevent increasing the size of future wheel builds
aws s3 mv "$wheel_file_path" "s3://$S3_BUCKET/artifacts/package_wheel_files/"
