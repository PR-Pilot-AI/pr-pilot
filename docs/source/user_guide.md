(userguide)=
# User Guide

Welcome to PR Pilot!

This guide will help you get started with PR Pilot and show you how to use it to automate your tasks.

## Installation

First, [install PR Pilot](https://github.com/apps/pr-pilot-ai) into your repository, then follow the instructions below to create and monitor tasks.

## Creating Tasks

PR Pilot is a **text-to-task** platform, which means you simply describe what you want to do in natural language, and PR Pilot will take care of the rest using its [capabilities](./capabilities.md).

You can give it new tasks in various ways.

### Github Comments

To create a task, simply comment on an issue or PR with the `/pilot` command followed by a description of the task you want to perform.


![First pilot command](img/first_command.png)

The bot will turn your comment into a link to your [dashboard](https://app.pr-pilot.ai), where you can monitor the task's progress.

### API

The PR Pilot API allows you to trigger tasks using your own tools and integrations.

1. Create a new API Key in the PR Pilot [dashboard](https://app.pr-pilot.ai/dashboard/api-keys/).
2. Use the API Key to authenticate your requests to the [PR Pilot API](https://app.pr-pilot.ai/api/swagger-ui/).

Example:
```bash
curl -X POST 'https://app.pr-pilot.ai/api/tasks/' \
-H 'Content-Type: application/json' \
-H 'X-Api-Key: YOUR_API_KEY_HERE' \
-d '{
    "prompt": "Properly format the README.md and add emojis",
    "github_repo": "owner/repo"
}'
```


### Python SDK

Install the [Python SDK](https://github.com/PR-Pilot-AI/pr-pilot-python) using pip:

```bash
pip install pr-pilot
```

Use the `create_task` and `get_task` functions to automate your Github project:

```python
import time

from pr_pilot.util import create_task, get_task

task = create_task("PR-Pilot-AI/pr-pilot", "Summarize the README file and create a Github issue with the result.")

while task.status != "completed":
    print(f"Waiting for task to complete. Status: {task.status}")
    task = get_task(task.id)
    time.sleep(5)
    
print(f"Task completed. Result:\n\n{task.result}")
```

The Python SDK works great for creating [powerful Github Actions](https://github.com/PR-Pilot-AI/pr-pilot/blob/main/.github/workflows/ai_task.py).

### Github Actions

You can create **[Smart Github Actions](https://github.com/PR-Pilot-AI/smart-actions)** by combining PR Pilot with Github Actions. 

For example, you can use the `format-issue` action to ensure that every new issue is properly formatted and labeled:

```yaml
# .github/workflows/issue_formatter.yaml`

name: Ensure new issue is properly formatted and labeled

on:
  issues:
    types: [opened]

jobs:
  format-issue:
    runs-on: ubuntu-latest
    steps:
      - name: Format GitHub Issue
        uses: PR-Pilot-AI/smart-actions/format-issue@v1
        with:

          # API key for PR Pilot must be defined as a secret in the repository
          api-key: ${{ secrets.PR_PILOT_API_KEY }}

          # Number of the issue to be formatted
          issue-number: ${{ github.event.issue.number }}

          # Customize the instructions to your needs
          formatting-instructions: |
            - Ensure the title begins with an appropriate emoji
            - Issue body should be properly Markdown-formatted
            - If the issue has no labels, add some
```

For your convenience, the `PR_PILOT_API_KEY` secret is set automatically on every project that uses PR Pilot.

### Dashboard

Soon you'll be able to create tasks directly from the [dashboard](https://app.pr-pilot.ai/dashboard/tasks/).

## Monitoring Tasks

While a task is running, **PR Pilot** will create events that you can follow in the [dashboard](https://app.pr-pilot.ai/dashboard/tasks/):

![PR Pilot](img/how_it_works_dashboard.png)

You'll also get a detailed overview of how your credits were spent.

![Monitoring PR Pilot](img/how_it_works_cost.png)