#!/bin/bash

# Iterate over documentation tickets and print their details
for row in $(jq -c '.[]' reports/doc_tickets.json); do
    issue_number=$(echo $row | jq -r '.issue_number')
    title=$(echo $row | jq -r '.title')
    url=$(echo $row | jq -r '.url')
    echo "Issue Number: $issue_number"
    echo "Title: $title"
    echo "URL: $url"
    echo "-------------------------"
done