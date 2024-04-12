<div align="center">
<img src="https://avatars.githubusercontent.com/ml/17635?s=140&v=" width="100" alt="PR Pilot Logo">
</div>

<p align="center">
  <a href="https://github.com/marketplace/pr-pilot-ai"><b>Install</b></a> |
  <a href="https://docs.pr-pilot.ai">Documentation</a> | 
  <a href="https://www.pr-pilot.ai/blog">Blog</a> | 
  <a href="https://www.pr-pilot.ai">Website</a>
</p>


# 🤖 PR Pilot

A **text-to-task platform** that enables GitHub developers to trigger AI-driven development tasks in their repositories from anywhere.

![PR Pilot](docs/source/img/overview.png)


Get started now with our [User Guide](https://docs.pr-pilot.ai/user_guide.html).


### 🌟 Use Natural Language Prompts to Automate Your GitHub Workflow

* [x] 🪄 [Quickly Generate Intial Implemenation / Fixes for Issues](https://github.com/PR-Pilot-AI/pr-pilot/issues/39#issuecomment-2028989177)
* [x] 🌐 [Automate Code Changes in PRs](https://docs.pr-pilot.ai/how_it_works.html#collaborate)
* [x] 🤔 [Ask questions about your issue/PR](https://docs.pr-pilot.ai/how_it_works.html#have-a-conversation)
* [x] 📝 [Generate Code Documentation](https://github.com/PR-Pilot-AI/pr-pilot/issues/51)
* [ ] Create PRs based on ChatGPT Conversations
* [ ] Create a Slack Bot for your Github Repo
* [ ] Trigger Code Changes from Zapier Workflows
* [ ] Create a New Task from a Python Script


Check out the [Demo Issues & PRs](https://github.com/PR-Pilot-AI/pr-pilot/issues?q=label:demo+is:closed+) to see how you can create tasks directly in Github. PR Pilot is actively involved in writing its own code! 

## 🛠️ Installation

You can install PR Pilot from the [GitHub Marketplace](https://github.com/marketplace/pr-pilot-ai).

## 🚀 Run Locally

Set the following environment variables:

| Variable                | Description                                  |
|-------------------------|----------------------------------------------|
| `GITHUB_APP_CLIENT_ID`  | GitHub App Client ID                         |
| `GITHUB_APP_SECRET`     | GitHub App Secret                            |
| `GITHUB_WEBHOOK_SECRET` | Secret for securing webhooks                 |
| `GITHUB_APP_ID`         | GitHub App ID                                |
| `OPENAI_API_KEY`        | API key for OpenAI services                  |
| `REPO_DIR`              | Directory for storing repository data        |
| `TAVILY_API_KEY`        | API key for Tavily search engine             |
| `STRIPE_API_KEY`        | Stripe API key for handling payments         |
| `STRIPE_WEBHOOK_SECRET` | Secret for securing Stripe webhook endpoints |
| `DJANGO_SECRET_KEY`     | Secret key for Django                        |

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
