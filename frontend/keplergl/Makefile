.PHONY: audit build clean e2e fix help lint setup snyk start test unit

build:    # compiles the code base
	@yarn build

clean:   # removes all build artifacts
	@rm -rf build/

e2e:  # runs the end-to-end tests
	@yarn e2e

fix:  # fixes lint issues
	@yarn fix

help:   # prints all make targets
	@cat Makefile | grep '^[^ ]*:' | grep -v '.PHONY' | grep -v help | sed 's/:.*#/#/' | column -s "#" -t

lint:  # lints all files
	@yarn lint

setup:   # prepares this code base after checkout
	@yarn install

start:   # runs the API
	@yarn start

test: build clean lint audit unit    # runs all tests

unit:   # runs the unit tests
	@yarn test

