.PHONY: setup build fix unit lint test start clean help
SHELL := /bin/bash
DIR := $(PWD)

DOCKER := $(shell ((test -e /proc/self/cgroup && grep -o -E '/docker/.+' < /proc/self/cgroup >/dev/null 2>&1) || (test -e /.dockerenv)); echo $$?)
ifeq ($(DOCKER), 0)
	export S3_ENDPOINT_URL = http://localstack:4566
else
	export S3_ENDPOINT_URL = http://localhost:4572
endif

export AWS_ACCESS_KEY_ID = makefile
export AWS_SECRET_ACCESS_KEY = localstack

setup: clean
	@pipenv install --dev

help:   # prints all make targets
	@cat Makefile | grep '^[^ ]*:' | grep -v '.PHONY' | grep -v help | sed 's/:.*#/#/' | column -s "#" -t

start: clean # runs the API
	ENVIRONMENT=development pipenv run uvicorn app.main:app --port 8000 --reload 

build:

unit:
	@pipenv run pytest -s .
	
lint: # lints all files
	echo "Running 'python linter'"
	@pipenv run flake8 --max-line-length=140
	@pipenv run autopep8 -d -a -r --max-line-length 140 --exit-code .
	@pipenv run black -l 140 --check .
	
fix:
	@pipenv run autopep8 -i -a -r --max-line-length 140 .
	@pipenv run black -l 140 .
	
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

docker-build:
	docker build -t ghcr.io/jvstinian/keplergl-s3/keplergl-s3-base:latest -f base.Dockerfile .
