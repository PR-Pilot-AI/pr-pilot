# PR Pilot

**[Documentation](https://docs.pr-pilot.ai)** | **[Website](https://www.pr-pilot.ai)** 

PR Pilot is a GitHub bot designed to autonomously understand and execute tasks based on commands in GitHub comments.
Use **`/pilot <prompt>`** in a comment and PR Pilot understands your prompt in the context of your issue/PR. 
What's currently possible:

* [**Request code changes**](https://docs.pr-pilot.ai/how_it_works.html#collaborate)
* [**Monitor its activities in a dashboard**](https://docs.pr-pilot.ai/how_it_works.html#monitor)
* [**Ask questions about your issue/PR**](https://docs.pr-pilot.ai/how_it_works.html#have-a-conversation)
* [**Rollback changes easily**](https://docs.pr-pilot.ai/how_it_works.html#rollback)
* [**Teach it about your project**](https://docs.pr-pilot.ai/how_it_works.html#teach)

See [how it works](https://docs.pr-pilot.ai/how_it_works.html) and check out the [usage examples](https://docs.pr-pilot.ai/how_it_works.html)!

## Installation 🛠️

You can install PR Pilot from the [GitHub Marketplace](https://github.com/marketplace/pr-pilot-ai).

## Run Locally 🚀

To get PR Pilot up and running on your own machine, follow these steps:

1. Install pip dependencies from `requirements.txt`.
```shell
pip install -r requirements.txt
```
2. Spin up a Postgres database for data persistence.
```shell
# Example using Docker
docker run --name postgres-pr-pilot -e POSTGRES_PASSWORD=postgres -d postgres
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

## Unit Tests 🧪

PR Pilot uses `tox` for managing unit tests. The test setup is configured in the `tox.ini` file, and tests are written using `pytest`.

To run the tests, execute the following command in your shell:
```shell
tox
```

This will run all the tests defined in the project, ensuring that your changes do not break existing functionality.

## Architecture 🏗️

At its core, it utilizes a **GitHub app** to facilitate interactions with GitHub repositories. 
The backbone of PR Pilot is a **Django** application, which is deployed to handle **GitHub webhooks**. 
This application processes the **`/pilot`** commands found in issue comments and pull requests and deploys Kubernetes jobs that 
execute the commands in the context of the repository.
For serving static files, PR Pilot employs an **nginx** server. To manage the deployment of the Django application, the 
nginx server, and the execution of jobs, PR Pilot relies on a **Kubernetes cluster**.


## Contributing 🤝

We welcome contributions to PR Pilot! Please check out our [contributing guidelines](CONTRIBUTING.md) for more information on how to get involved.

## License 📄

PR Pilot is open source and available under the GPL-3 License. See the [LICENSE](LICENSE) file for more info.
