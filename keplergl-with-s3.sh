#!/usr/bin/env bash
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

display_help() {
  cat << EOF
Name:
  keplergl-with-s3 - CLI tool for this project

Commands:
  shell                    - brings up an interactive bash shell on the docker CI image
  build BASE_IMAGE         - builds a base image locally
  initialize               - installs yarn packages for web servers and builds base images
EOF
}

if [ "$#" -eq 0 ]; then
  display_help
  exit 1
fi

COMMAND="$1"
case "$COMMAND" in
  initialize)
    "$DIR/scripts/setup-local-node-servers.sh"
    source "$DIR/scripts/package-base-images.sh" && build_all_base_images
  ;;
  *)
    display_help
    echo -e "Unknown Command: $COMMAND\\n"
    exit 1
esac
