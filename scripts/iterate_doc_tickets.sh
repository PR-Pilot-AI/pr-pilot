#!/bin/bash

# Iterate over documentation tickets using jq

tickets=$(jq -c '.[]' reports/doc_tickets.json)

for ticket in $tickets; do
    issue_number=$(echo $ticket | jq -r '.issue_number')
    title=$(echo $ticket | jq -r '.title')
    url=$(echo $ticket | jq -r '.url')
    echo "Issue #$issue_number: $title"
    echo "URL: $url"
    echo "-------------------------"

done