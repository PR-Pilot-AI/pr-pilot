#!/bin/bash

# Check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, please install it to use this script."
    exit
fi

# Iterate over bug tickets
for row in $(jq -c '.[]' reports/bug_tickets.json); do
    id=$(echo $row | jq -r '.id')
    title=$(echo $row | jq -r '.title')
    echo "Bug ID: $id"
    echo "Title: $title"
    echo "-------------------------"
done
