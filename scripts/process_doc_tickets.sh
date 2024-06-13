#!/bin/bash

# Check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, please install jq to use this script."
    exit
fi

# Read the JSON file and iterate over the issues
cat reports/doc_tickets.json | jq -c '.[]' | while read -r issue; do
    issue_number=$(echo "$issue" | jq -r '.issue_number')
    title=$(echo "$issue" | jq -r '.title')
    url=$(echo "$issue" | jq -r '.url')
    echo "Issue #$issue_number: $title"
    echo "URL: $url"
    echo "-----------------------------"
done