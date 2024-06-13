#!/bin/bash

# Check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, please install jq to use this script."
    exit
fi

# Read the JSON file
file="reports/bug_tickets.json"

# Check if the file exists
if [ ! -f "$file" ]; then
    echo "$file does not exist."
    exit 1
fi

# Iterate over the bug tickets
jq -c '.[]' "$file" | while read -r ticket; do
    echo "Processing ticket: $ticket"
    # Add your processing logic here
done
