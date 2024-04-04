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

An open source Github bot that allows developers to generate code, issues and pull requests directly from comments.

### 📝 PR Pilot is actively involved in [writing its own code](https://github.com/PR-Pilot-AI/pr-pilot/issues?q=label:demo+is:closed+)
* 🛠️ [Setting up Unit Testing](https://github.com/PR-Pilot-AI/pr-pilot/issues/39)
* 📄 [Creating a README file](https://github.com/PR-Pilot-AI/pr-pilot/issues/35)
* 😊 [Adding Emojis and correcting grammar](https://github.com/PR-Pilot-AI/pr-pilot/issues/47)
* 📄 [Documenting the Domain Model (incl. Class Diagram)](https://github.com/PR-Pilot-AI/pr-pilot/issues/51)

### 🌟 Features

* 🌐 [**Use PR Pilot to work on PRs**](https://docs.pr-pilot.ai/how_it_works.html#collaborate)
* 📊 [**Monitor its activities in a dashboard**](https://docs.pr-pilot.ai/how_it_works.html#monitor)
* 🤔 [**Ask questions about your issue/PR**](https://docs.pr-pilot.ai/how_it_works.html#have-a-conversation)
* ⏪ [**Rollback changes easily**](https://docs.pr-pilot.ai/how_it_works.html#rollback)
* 🎓 [**Teach it about your project**](https://docs.pr-pilot.ai/how_it_works.html#teach)

See [how it works in detail](https://docs.pr-pilot.ai/how_it_works.html) and check out more [usage examples](https://docs.pr-pilot.ai/examples.html)!

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
