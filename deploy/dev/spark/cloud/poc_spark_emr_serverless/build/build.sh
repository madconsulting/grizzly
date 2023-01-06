# -- Inputs
PYTHON_VERSION="3.9.12"
PYTHON_VERSION_SHORT="3.9"
POETRY_VERSION="1.2.0b3"
S3_BUCKET="poc-spark-emr-serverless-dev-bucket-316fb28"
echo "Inputs to deploy Spark cloud env to s3:"
echo "PYTHON_VERSION=$PYTHON_VERSION"
echo "PYTHON_VERSION_SHORT=$PYTHON_VERSION_SHORT"
echo "POETRY_VERSION=$POETRY_VERSION"
echo "S3_BUCKET=$S3_BUCKET"

# -- Build the custom venv and package wheel files from Poetry in Docker (with BuildKit backend)
echo "Building the custom venv and package wheel files from Poetry in Docker (with BuildKit backend)"
DOCKER_BUILDKIT=1 docker build \
  --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
  --build-arg PYTHON_VERSION_SHORT="${PYTHON_VERSION_SHORT}" \
  --build-arg POETRY_VERSION="${POETRY_VERSION}" \
  -f deploy/dev/spark/cloud/poc_spark_emr_serverless/build/Dockerfile \
  --output . .

# -- Upload the virtual environment to S3
echo "Adding Poetry package version to venv file name"
script="deploy/dev/spark/cloud/poc_spark_emr_serverless/build/build_artifacts_interactions.py"
function="add_package_version_to_venv"
python_run_command="poetry run python3 $script $function"
echo "Python command to add the package version to the venv file name: $python_run_command"
# Reading output from STDOUT
venv_file_path=$($python_run_command)
echo "Venv file: $venv_file_path"
echo "Uploading the virtual environment to S3"
aws s3 cp ${venv_file_path} s3://${S3_BUCKET}/artifacts/venvs/

# -- Upload the wheel file to S3
echo "Retrieving Poetry wheel file already generated by Poetry in Docker"
function="rename_poetry_wheel_file"
python_run_command="poetry run python3 $script $function"
echo "Python command to rename the wheel file: $python_run_command"
# Reading output from STDOUT
wheel_file_path=$($python_run_command)
echo "Wheel file: $wheel_file_path"
echo "Uploading the wheel file to S3"
aws s3 cp ${wheel_file_path} s3://${S3_BUCKET}/artifacts/package_wheel_files/
