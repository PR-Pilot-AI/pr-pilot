#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Read the JSON file and iterate over the issues
cat reports/doc_tickets.json | jq -c '.[]' | while read -r issue; do
    # Extract issue details using jq
    issue_number=$(echo "$issue" | jq -r '.issue_number')
    title=$(echo "$issue" | jq -r '.title')
    url=$(echo "$issue" | jq -r '.url')

    # Print the issue details
    echo "Issue Number: $issue_number"
    echo "Title: $title"
    echo "URL: $url"
    echo "-------------------------"

    # Add any additional processing here

    # Handle special characters in the title
    safe_title=$(echo "$title" | sed 's/[^a-zA-Z0-9]/_/g')
    echo "Safe Title: $safe_title"
    echo "========================="

    # Example of using the safe title in a command
    # touch "processed_issues/$safe_title.txt"

done