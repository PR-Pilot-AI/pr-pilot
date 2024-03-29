# PR Pilot 🚀

PR Pilot is a GitHub bot designed to autonomously understand and execute tasks based on commands in GitHub comments. It leverages the power of Django, Python, Docker, and Kubernetes to provide a seamless experience for managing GitHub projects. For more information, visit our [documentation](https://docs.pr-pilot.ai) and the official website at [www.pr-pilot.ai](https://www.pr-pilot.ai).

## Architecture 🏗️

PR Pilot operates on a robust architecture that includes:

- A registered [GitHub app](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps) to interact with GitHub repositories.
- A Django application deployed to receive GitHub webhooks, processing commands found in issue comments and pull requests.
- An nginx server for serving static files efficiently.
- Jobs triggered by webhooks to execute `/pilot` commands within the GitHub environment.
- A Kubernetes cluster that orchestrates the deployment of the Django app, nginx server, and job execution.

## How to Run 🚀

To get PR Pilot up and running, follow these steps:

1. Install pip dependencies from `requirements.txt`.
2. Spin up a Postgres database for data persistence.
3. Start ngrok to expose your local server to the internet and set the GitHub app webhook endpoint and OAuth login callback accordingly.
4. Set the following environment variables: `GITHUB_APP_CLIENT_ID`, `GITHUB_APP_SECRET`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_APP_ID`, `OPENAI_API_KEY`, `REPO_DIR`, `TAVILY_API_KEY`, `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`.
5. Run the Django application using the command `python manage.py runserver`.

## Contributing 🤝

We welcome contributions to PR Pilot! Please check out our [contributing guidelines](CONTRIBUTING.md) for more information on how to get involved.

## License 📄

PR Pilot is open source and available under the MIT License. See the [LICENSE](LICENSE) file for more info.