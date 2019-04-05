#!/usr/bin/env bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

python3.7 "rest/main.py" >/dev/null 2>&1 &
rest_pid=$!

sleep 2s

kill -SIGINT $rest_pid
exit 0
