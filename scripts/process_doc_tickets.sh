#!/bin/bash

# Read the JSON file
json_file="reports/doc_tickets.json"

# Check if the file exists
if [[ ! -f "$json_file" ]]; then
  echo "File $json_file does not exist."
  exit 1
fi

# Iterate over the JSON array and print issue numbers
jq -c '.[]' "$json_file" | while read -r issue; do
  issue_number=$(echo "$issue" | jq -r '.issue_number')
  echo "Processing issue number: $issue_number"
done