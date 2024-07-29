# Create Your Own GitHub Application

## Step 1: Create Your GitHub Application

Follow the official GitHub documentation to [register a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app#registering-a-github-app).

## Step 2: Configure Your GitHub App

### Required Configuration

#### General Settings

- **Callback URL**: Enter the URL of your PR-Pilot application.
- **Webhook URL**: Enter the URL of your PR-Pilot application, appending `/webhooks/github/` to the end.
- **Webhook Secret**: This should match the value of the `GITHUB_WEBHOOK_SECRET` environment variable.

#### Repository Permissions

Set the following repository permissions for your GitHub App:

| Permission              | Access Level  |
|-------------------------|---------------|
| Checks                  | Read-only     |
| Code scanning alerts    | Read-only     |
| Commit statuses         | Read-only     |
| Contents                | Read and Write|
| Dependabot alerts       | Read-only     |
| Discussions             | Read and Write|
| Metadata                | Read-only     |
| Projects                | Read and Write|
| Pull requests           | Read and Write|
| Secrets                 | Read and Write|

#### Subscribe to Events

Ensure your GitHub App is subscribed to the following events:

- Commit comment
- Discussion
- Discussion comment
- Issue comment
- Issues
- Pull request review
- Pull request review comment
- Pull request review thread

## Step 3: Configure PR-Pilot Application

Set the following environment variables in your PR-Pilot application:

| Variable                | Description                      |
|-------------------------|----------------------------------|
| `GITHUB_APP_CLIENT_ID`  | Your GitHub App Client ID        |
| `GITHUB_APP_SECRET`     | Your GitHub App Secret           |
| `GITHUB_WEBHOOK_SECRET` | Secret for securing webhooks     |
| `GITHUB_APP_ID`         | Your GitHub App ID               |

## Step 4: Generate GitHub App Private Key

Generate a private key for your GitHub App by following [this guide](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps#generating-private-keys). Save the private key file as `github_app_private_key.pem` in the directory where you run the PR-Pilot application.
