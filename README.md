# PR Pilot 🚀

PR Pilot is a GitHub bot designed to autonomously understand and execute tasks based on commands in GitHub comments. It leverages the power of Django, Python, Docker, and Kubernetes to provide a seamless experience for managing GitHub projects. For more information, visit our [documentation](https://docs.pr-pilot.ai) and the official website at [www.pr-pilot.ai](https://www.pr-pilot.ai).

## Architecture 🏗️

The architecture of PR Pilot is designed for robustness and efficiency. At its core, it utilizes a GitHub app, registered according to GitHub's guidelines, to facilitate interactions with GitHub repositories. The backbone of PR Pilot is a Django application, which is deployed to handle GitHub webhooks. This application processes commands found in issue comments and pull requests, ensuring that tasks are executed as intended.

For serving static files, PR Pilot employs an nginx server, known for its high performance and stability. The system also includes jobs that are triggered by webhooks to carry out `/pilot` commands directly within the GitHub environment. To manage the deployment of the Django application, the nginx server, and the execution of jobs, PR Pilot relies on a Kubernetes cluster. This setup ensures that the application is scalable, resilient, and can efficiently manage the workload.

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
