#!/bin/bash

# Iterate over documentation tickets using jq
cat reports/doc_tickets.json | jq -c '.[]' | while read -r ticket; do
    echo "Processing ticket: $ticket"
    # You can add more processing logic here
    issue_number=$(echo "$ticket" | jq -r '.issue_number')
    title=$(echo "$ticket" | jq -r '.title')
    url=$(echo "$ticket" | jq -r '.url')
    echo "Issue Number: $issue_number"
    echo "Title: $title"
    echo "URL: $url"
    echo "-------------------------"

done