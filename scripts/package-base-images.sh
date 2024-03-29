#!/usr/bin/env bash
set -euo pipefail

# Helper functions for building docker base images

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

: "${CI_COMMIT_SHA:=head}"
: "${CI_REGISTRY_IMAGE:="ghcr.io/jvstinian/keplergl-with-s3"}"

get_image_name() {
  local context="$1"
  local dockerfile="${2:-Dockerfile}"
  local name="${context##*/}"
  local modifier
  modifier="$(echo "$dockerfile" | cut -d "." -f1)"
  if [ "$modifier" != "$dockerfile" ]; then
    name="$name-$modifier"
  fi
  echo "$name"
  return
}

get_image_tag() {
  local name
  name=$(get_image_name "$@")
  local image="$CI_REGISTRY_IMAGE/$name"
  echo "$image"
  return
}

build_image() {
  local context="$1"
  local dockerfile="${2:-Dockerfile}"
  local trigger="^$context/$dockerfile${3:+|^$context/$3}"

  local image
  image=$(get_image_tag "$1" "$2")
  
  echo "Building $image with regex trigger '$trigger'"
  pushd "$DIR/../$context" > /dev/null
  docker build --no-cache --pull -t "$image:latest" -f "$dockerfile" .
  popd > /dev/null
}

build_all_base_images() {
  while read -r line
  do 
    build_image $line
  done < "$DIR/docker-image-specs.txt"
}
