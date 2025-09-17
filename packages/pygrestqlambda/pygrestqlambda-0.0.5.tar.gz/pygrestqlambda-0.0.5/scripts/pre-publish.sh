#!/bin/bash
set -euo pipefail

# Override pyproject version if environment variable is set
PROJECT_VERSION=${PROJECT_VERSION:=0.0.0}
echo "Setting project version: ${PROJECT_VERSION}"
sed -i -e "s/version.*=.*\".*\"/version = \"${PROJECT_VERSION}\"/" pyproject.toml
