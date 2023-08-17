#!/usr/bin/env bash
set -euo pipefail

# This script is run as an initialization hook when the localstack container enters state READY.
# This script sets up S3 buckets with the files needed.

pushd "/opt/localstack-data/s3" > /dev/null
find . -maxdepth 1 ! -path . -type d | sed 's/.\//s3:\/\//' | xargs -I {} awslocal s3 mb {}
find . -type f | sed 's/.\///' | xargs -I {} awslocal s3 mv {} s3://{}
popd > /dev/null
