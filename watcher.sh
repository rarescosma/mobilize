#!/usr/bin/env sh

WATCH_DIR="${WATCH_DIR:-$(pwd)/workdir}"
OUT_DIR="${OUT_DIR:-$(pwd)/workdir}"

echo ">>> Starting watchexec on ${WATCH_DIR}"
watchexec --emit-events-to=json-stdio \
  -w "${WATCH_DIR}" -e "url" \
  -o queue \
  -p "mobilize ${OUT_DIR} -"
