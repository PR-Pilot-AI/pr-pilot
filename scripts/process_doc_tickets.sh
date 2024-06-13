#!/bin/bash

# Path to the JSON file
json_file="reports/doc_tickets.json"

# Check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, please install jq to use this script."
    exit
fi

# Iterate over each issue in the JSON file
jq -c '.[]' "$json_file" | while read -r issue; do
    issue_number=$(echo "$issue" | jq -r '.issue_number')
    title=$(echo "$issue" | jq -r '.title')
    url=$(echo "$issue" | jq -r '.url')
    echo "Issue #$issue_number: $title"
    echo "URL: $url"
    echo "-----------------------------"
done