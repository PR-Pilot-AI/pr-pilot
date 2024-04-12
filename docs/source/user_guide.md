(userguide)=
# User Guide

Welcome to PR Pilot!

This guide will help you get started with PR Pilot and show you how to use it to automate your tasks.

## Installation

First, install PR Pilot into your repository from the [Github marketplace](https://github.com/apps/pr-pilot-ai)

## Creating Tasks

PR Pilot is a **text-to-task** platform, which means you simply describe what you want to do in natural language, and PR Pilot will take care of the rest using its [capabilities](./capabilities.md).

You can create tasks via Github comments, the dashboard, or the API.

### via Github Comments

To create a task, simply comment on an issue or PR with the `/pilot` command followed by a description of the task you want to perform.


![First pilot command](img/first_command.png)

The bot will turn your comment into a link to your [dashboard](https://app.pr-pilot.ai), where you can monitor the task's progress.


### via the Dashboard

(Coming Soon)

### via the API

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

### via Slack

(coming soon)

### via Zapier

(coming soon)

## Monitoring Tasks

While a task is running, **PR Pilot** will create events that you can follow in the [dashboard](https://app.pr-pilot.ai/dashboard/tasks/):

![PR Pilot](img/how_it_works_dashboard.png)

You'll also get a detailed overview of how your credits were spent.

![Monitoring PR Pilot](img/how_it_works_cost.png)