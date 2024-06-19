<div align="center">
<img src="https://avatars.githubusercontent.com/ml/17635?s=140&v=" width="100" alt="PR Pilot Logo">
</div>

<p align="center">
  <a href="https://github.com/apps/pr-pilot-ai/installations/new"><b>Install</b></a> |
  <a href="https://docs.pr-pilot.ai">Documentation</a> | 
  <a href="https://www.pr-pilot.ai/blog">Blog</a> | 
  <a href="https://www.pr-pilot.ai">Website</a>
</p>

# PR Pilot

[![Build Status](https://github.com/PR-Pilot-AI/pr-pilot/actions/workflows/unit_tests.yml/badge.svg?branch=main)](https://github.com/PR-Pilot-AI/pr-pilot/actions/workflows/unit_tests.yml)                                    │
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)                                                                                                                                                                     │
![Django](https://img.shields.io/badge/Django-5.0.3-green)                                                                                                                                                                     │
![License](https://img.shields.io/badge/License-GPL--3.0-blue)                                                                                                                                                                 │
![Version](https://img.shields.io/badge/Version-1.4.10-orange)

Save time and stay in the flow by delegating routine work to AI with confidence and predictability. PR Pilot assist you in your daily workflow and works with the dev tools you trust and love - exactly when and where you want it.

[![asciicast](https://asciinema.org/a/664029.svg)](https://asciinema.org/a/664029)

Get started now with our [User Guide](https://docs.pr-pilot.ai/user_guide.html).


### Hand of work to PR Pilot from anywhere

You can interact with PR Pilot in a variety of ways:

#### Using the **[Command-Line Interface](https://github.com/PR-Pilot-AI/pr-pilot-cli)**

```bash
pilot edit main.py "Add docstrings to all functions and classes"
```

With [prompt templates](https://github.com/PR-Pilot-AI/pr-pilot-cli/tree/main/prompts), you can create powerful,
reusable commands:

```markdown
I've made some changes and opened a new PR: #{{ env('PR_NUMBER') }}.

I need a PR title and a description that summarizes these changes in short, concise bullet points.
The PR description will also be used as merge commit message, so it should be clear and informative.

Use the following guidelines:

- Start title with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- At the very top, provide 1-sentence summary of the changes and their impact.
- Below, list the changes made in bullet points.

# Your task
Edit PR #{{ env('PR_NUMBER') }} title and description to reflect the changes made in this PR.
```

Send PR Pilot off to give any PR a title and description according to your guidelines:

```bash
PR_NUMBER=153 pilot task -f generate-pr-description.md.jinja2
```

#### Using the **[Python SDK](https://github.com/PR-Pilot-AI/pr-pilot-python)**:

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

#### Using the **[REST API](https://app.pr-pilot.ai/api/redoc/)**:

```bash 
curl -X POST 'https://app.pr-pilot.ai/api/tasks/' \
-H 'Content-Type: application/json' \
-H 'X-Api-Key: YOUR_API_KEY_HERE' \
-d '{
    "prompt": "Properly format the README.md and add emojis",
    "github_repo": "owner/repo"
}'
```


#### Using **[Smart Workflows](https://github.com/PR-Pilot-AI/smart-workflows)**:

```yaml
# .github/workflows/chat_bot.yaml`

name: "🤖 My Project's Custom Chat Bot"

on:
  issues:
    types: [labeled, commented]
  issue_comment:
    types: [created]

jobs:
  handle-chat:
    if: >
      (github.event.label.name == 'chat' || contains(github.event.issue.labels.*.name, 'chat')) &&
      github.event.sender.login != 'pr-pilot-ai[bot]'
    runs-on: ubuntu-latest
    steps:
      - name: AI Chat Response
        uses: PR-Pilot-AI/smart-actions/quick-task@v1
        with:
          api-key: ${{ secrets.PR_PILOT_API_KEY }}
          agent-instructions: |
              @${{ github.event.sender.login }} commented on issue #${{ github.event.issue.number }}.
              Read the content of issue #${{ github.event.issue.number }}.
              If there are no comments yet, add a comment that makes sense in the context of the issue.
              If there are comments, provide a response to the latest comment.
```


#### or talk to PR Pilot directly on **[Github issues and PRs](https://github.com/PR-Pilot-AI/pr-pilot/issues?q=label:demo+)**:

![First pilot command](docs/source/img/first_command.png)

Check our **[roadmap](https://docs.pr-pilot.ai/roadmap.html)** for what's to come!

## 🛠️ Installation

To get started, follow our [User Guide](https://docs.pr-pilot.ai/user_guide.html).

## 🚀 Run Locally

Set the following environment variables:

| Variable                | Description                                                     |
|-------------------------|-----------------------------------------------------------------|
| `GITHUB_APP_CLIENT_ID`  | GitHub App Client ID                                            |
| `GITHUB_APP_SECRET`     | GitHub App Secret                                               |
| `GITHUB_WEBHOOK_SECRET` | Secret for securing webhooks                                    |
| `GITHUB_APP_ID`         | GitHub App ID                                                   |
| `OPENAI_API_KEY`        | API key for OpenAI services                                     |
| `REPO_DIR`              | Directory for storing repository data                           |
| `TAVILY_API_KEY`        | API key for Tavily search engine                                |
| `STRIPE_API_KEY`        | Stripe API key for handling payments                            |
| `STRIPE_WEBHOOK_SECRET` | Secret for securing Stripe webhook endpoints                    |
| `DJANGO_SECRET_KEY`     | Secret key for Django                                           |
| `SENTRY_DSN`            | (Optional) Sentry DSN for error monitoring                      |
| `JOB_STRATEGY`          | (Optional) Strategy for running jobs ('thread', 'redis', 'log') |
| `REDIS_HOST`            | (Optional) Redis host for job scheduling                        |
| `REDIS_PORT`            | (Optional) Redis port for job scheduling                        |
| `REPO_CACHE_DIR`        | (Optional) Directory for storing repository cache               |
| `REPO_DIR`              | (Optional) Workspace for storing repo in worker                 |
| `SLACK_APP_ID`          | Slack App ID               |
| `SLACK_CLIENT_ID`       | Slack Client ID            |
| `SLACK_CLIENT_SECRET`   | Slack Client Secret        |
| `SLACK_SIGNING_SECRET`  | Slack Signing Secret       |

To get PR Pilot up and running on your own machine, follow these steps:


```bash
# Clone the repository
git clone https://github.com/PR-Pilot-AI/pr-pilot.git

# Change directory
cd pr-pilot

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

To expose your local server to the internet, you can use `ngrok`:

```bash
ngrok http 8000
```

## 🧪 Unit Tests

PR Pilot uses `tox` for managing unit tests. The test setup is configured in the `tox.ini` file, and tests are written using `pytest`.

To run the tests, execute:

```bash
tox
```

This will run all the tests defined in the project, ensuring that your changes do not break existing functionality.

## 📚 Code Documentation

For more information on the code structure and documentation, please visit [docs/code](docs/code).

## 🤝 Contributing

We welcome contributions to PR Pilot! Please check out our [contributing guidelines](CONTRIBUTING.md) for more information on how to get involved.

## 📄 License

PR Pilot is open source and available under the GPL-3 License. See the [LICENSE](LICENSE) file for more info.
