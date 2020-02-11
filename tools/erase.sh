#!/usr/bin/env bash

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/.."

source variables.sh
