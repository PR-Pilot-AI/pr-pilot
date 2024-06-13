#!/bin/bash

# Iterate over documentation tickets and print details
for row in $(jq -c '.[]' reports/doc_tickets.json); do
    issue_number=$(echo $row | jq -r '.issue_number')
    title=$(echo $row | jq -r '.title')
    url=$(echo $row | jq -r '.url')
    echo "Issue #$issue_number: $title"
    echo "URL: $url"
    echo "-------------------------"
done