#!/bin/bash

if [ $# -lt 2 ]; then
    echo "usage: extract-image.sh IMAGE_NAME DEST_DIR"
    exit 1
fi

set -euo pipefail

IMAGE_NAME="$1"
DEST_DIR="$2"

[ -d "$DEST_DIR" ] && rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

cid=$( docker create $IMAGE_NAME true )
docker export $cid | tar -C "$DEST_DIR" -xf -
docker rm -fv $cid
