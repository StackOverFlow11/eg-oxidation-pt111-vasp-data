#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
sha256sum -c manifest/checksums.sha256
