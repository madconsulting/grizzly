# -- Software Stack Version

PYTHON_VERSION="3.9.12"
PYTHON_VERSION_SHORT="3.9"
POETRY_VERSION="1.2.0b3"
S3_BUCKET="poc-spark-emr-serverless-dev-bucket-7cb2462"

# -- Building the custom venv with BuildKit backend

DOCKER_BUILDKIT=1 docker build \
  --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
  --build-arg PYTHON_VERSION_SHORT="${PYTHON_VERSION_SHORT}" \
  --build-arg POETRY_VERSION="${POETRY_VERSION}" \
  -f deploy/dev/spark/cloud/poc_spark_emr_serverless/build_venv/Dockerfile \
  --output . .

# -- Upload the artifacts to S3
aws s3 cp pyspark_${PYTHON_VERSION}.tar.gz     s3://${S3_BUCKET}/artifacts/pyspark_venv/