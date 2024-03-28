#!/usr/bin/env bash
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

setup_local_node_server() {
  local webserver_dir="$1"
  local docker_image="$2"
  local name="${webserver_dir##*/}"

  pushd "$DIR/../$webserver_dir" > /dev/null
  docker run -v "$(pwd):/opt/$name" --workdir "/opt/$name" --entrypoint /bin/sh -t "$docker_image" -c 'PATH=/usr/local/bin:$PATH yarn install'
  popd > /dev/null
}

setup_local_node_server frontend/keplergl node:14-alpine

