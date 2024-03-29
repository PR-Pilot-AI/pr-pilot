# PR Pilot 🚀

PR Pilot is a GitHub bot designed to autonomously understand and execute tasks based on commands in GitHub comments. It leverages the power of Django, Python, Docker, and Kubernetes to provide a seamless experience for managing GitHub projects. For more information, visit our [documentation](https://docs.pr-pilot.ai) and the official website at [www.pr-pilot.ai](https://www.pr-pilot.ai).

## Architecture 🏗️

The architecture of PR Pilot is designed for robustness and efficiency. At its core, it utilizes a GitHub app, registered according to GitHub's guidelines, to facilitate interactions with GitHub repositories. The backbone of PR Pilot is a Django application, which is deployed to handle GitHub webhooks. This application processes commands found in issue comments and pull requests, ensuring that tasks are executed as intended.

For serving static files, PR Pilot employs an nginx server, known for its high performance and stability. The system also includes jobs that are triggered by webhooks to carry out `/pilot` commands directly within the GitHub environment. To manage the deployment of the Django application, the nginx server, and the execution of jobs, PR Pilot relies on a Kubernetes cluster. This setup ensures that the application is scalable, resilient, and can efficiently manage the workload.

## How to Run 🚀

To get PR Pilot up and running, follow these steps:

1. Install pip dependencies from `requirements.txt`.
```shell
pip install -r requirements.txt
```
2. Spin up a Postgres database for data persistence.
```shell
# Example using Docker
docker run --name postgres-pr-pilot -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```
3. Start ngrok to expose your local server to the internet and set the GitHub app webhook endpoint and OAuth login callback accordingly.
```shell
ngrok http 8000
```
4. Set the following environment variables:

| Variable                | Description                                   |
|-------------------------|-----------------------------------------------|
| `GITHUB_APP_CLIENT_ID`  | GitHub App Client ID                          |
| `GITHUB_APP_SECRET`     | GitHub App Secret                             |
| `GITHUB_WEBHOOK_SECRET` | Secret for securing webhooks                  |
| `GITHUB_APP_ID`         | GitHub App ID                                 |
| `OPENAI_API_KEY`        | API key for OpenAI services                   |
| `REPO_DIR`              | Directory for storing repository data         |
| `TAVILY_API_KEY`        | API key for Tavily search engine              |
| `STRIPE_API_KEY`        | Stripe API key for handling payments          |
| `STRIPE_WEBHOOK_SECRET` | Secret for securing Stripe webhook endpoints  |

5. Run the Django application using the command `python manage.py runserver`.
```shell
python manage.py runserver
```

## Contributing 🤝

We welcome contributions to PR Pilot! Please check out our [contributing guidelines](CONTRIBUTING.md) for more information on how to get involved.

## License 📄

PR Pilot is open source and available under the MIT License. See the [LICENSE](LICENSE) file for more info.