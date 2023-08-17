.PHONY: setup build fix unit lint test start clean help
SHELL := /bin/bash
DIR := $(PWD)

# TODO: Check the following
# DOCKER := $(shell test -e /proc/self/cgroup && grep -o -E '/docker/.+' < /proc/self/cgroup >/dev/null 2>&1; echo $$?)
# ifeq ($(DOCKER), 0)
# 	export S3_ENDPOINT_URL = http://localstack:4572
# else
# 	export S3_ENDPOINT_URL = http://localhost:4572
# endif

export AWS_ACCESS_KEY_ID = makefile
export AWS_SECRET_ACCESS_KEY = localstack

setup: clean
	@pipenv install --dev

help:   # prints all make targets
	@cat Makefile | grep '^[^ ]*:' | grep -v '.PHONY' | grep -v help | sed 's/:.*#/#/' | column -s "#" -t

start: clean # runs the API
	ENVIRONMENT=development pipenv run uvicorn app.main:app -- port 8000 --reload 

build:

# TODO: Add pytest
unit:
	
# TODO: Add linting
lint: clean # lints all files
	
# TODO: Add fix
fix:
	
test: build clean lint unit # runs all tests

clean:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .eggs/
	@find . -name '.pytest_cache' -type d -exec rm -rf {} +

# TODO: Will this be needed?
# localstack: # bring up localstack
# 	@../../../scripts/setup-test-localstack.sh

docker-build:
	docker build -t ghcr.io/jvstinian/keplergl-s3/keplergl-s3-base:latest -f base.Dockerfile .