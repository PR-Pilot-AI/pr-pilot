(user_guide)=
# User Guide
PR Pilot is designed for you to save time and to help you stay in the flow. 
The CLI lets you to delegate routine work to AI with confidence and predictability. 

This guide will help you understand how to use PR Pilot with your Github project.
## Installation

If you haven't done so, [install PR Pilot](https://github.com/apps/pr-pilot-ai/installations/new) into your repository.

## The Basics

Every interaction between you and PR Pilot is a task. Tasks are created using prompts.

You and your tools can interact with PR Pilot using natural language,
supported by a variety of tools and integrations.
Which one is best for you highly depends on your specific use case. On [YouTube](https://www.youtube.com/watch?v=HVcW3ceqtfw&list=PLDz7ICzRy18wEgi70CPqsaCoNVSEw1GI9), 
we provide examples of how to use PR Pilot in different scenarios.

## Command-Line Interface
Our [CLI](https://github.com/PR-Pilot-AI/pr-pilot-cli) puts PR Pilot right at your fingertips:

```bash
brew tap pr-pilot-ai/homebrew-tap
brew install pr-pilot-cli
```

Open a terminal and `ls` into a repository you have installed PR Pilot, then
use the `pilot` command:

```bash
pilot edit main.py "Make sure all functions and classes have docstrings."
```

For more details, head over to the [CLI Documentation](https://github.com/PR-Pilot-AI/pr-pilot-cli). 

### File Changes, Branches and Pull Requests
By default, whenever PR Pilot creates or edits files,
it will create a new branch and open a pull request for you.

For example:

```bash
pilot task "Edit the README.md file: Add emojis to all headers"
```

will result in a new branch and a pull request with the changes.

However, you can also edit local files directly:

```bash
pilot edit README.md "Add emojis to all headers"
```

This will not create a branch or a pull request, but will edit the file in-place.

### Configuration and Customization

To customize PR Pilot's behavior, use `~/.pr-pilot.yaml`:

```yaml
# Your API Key from https://app.pr-pilot.ai/dashboard/api-keys/
api_key: YOUR_API_KEY

# Default Github repository if not running CLI in a repository directory
default_repo: owner/repo

# Enable --sync by default
auto_sync: true

# Suppress status messages by default
vebose: false
```



## Python SDK

To use PR Pilot in your own tools and integrations, you can use the [Python SDK](https://github.com/PR-Pilot-AI/pr-pilot-python):

```bash
pip install pr-pilot
```

Use the `create_task`, `get_task` and `wait_for_result` functions to automate your Github project:

```python
from pr_pilot.util import create_task, wait_for_result

prompt = """
1. Find all 'bug' issues created yesterday on Slack and Linear.
2. Summarize and post them to #bugs-daily on Slack
3. Save the summary in `reports/<date>.md`
"""

github_repo = "PR-Pilot-AI/pr-pilot"
task = create_task(github_repo, prompt)
result = wait_for_result(task)

print(result)
```

The Python SDK works great for creating [powerful Github Actions](https://github.com/PR-Pilot-AI/smart-actions).


### Using the REST API

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

### Talk to the Agent in Github Comments

PR Pilot will create issues and PRs for you. To stay in the flow, just use the `/pilot` command followed by a description of the task you want to perform.


![First pilot command](img/first_command.png)

The bot will turn your comment into a link to your [dashboard](https://app.pr-pilot.ai), where you can monitor the task's progress.

### Smart Github Actions

If you're comfortable with Github Actions and want to create your own automations, you can use our **[Smart Actions](https://github.com/PR-Pilot-AI/smart-actions)** to create your own workflows.
These actions are hand-crafted using state-of-the-art prompt engineering techniques and let you automate your Github projects in powerful new ways.



## Monitoring Tasks

While a task is running, **PR Pilot** will create events that you can follow in the [dashboard](https://app.pr-pilot.ai/dashboard/tasks/):

![PR Pilot](img/how_it_works_dashboard.png)

You'll also get a detailed overview of how your credits were spent.

![Monitoring PR Pilot](img/how_it_works_cost.png)