#!/usr/bin/env bash

# Start all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# Start the REST server
python3.7 "rest/main.py" >/dev/null 2>&1 &
rest_pid=$!

# Clean up - kill the REST server by sending a keyboard interrupt signal
kill -SIGINT $rest_pid
exit 0
