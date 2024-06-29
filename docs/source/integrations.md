# Integrations

PR Pilot integrates with your favorite tools and services to avoid context switching and streamline your workflow. By connecting PR Pilot with other platforms, you can automate repetitive tasks, improve collaboration, and enhance your development process. 
You can add new integrations using the [dashboard](https://app.pr-pilot.ai/dashboard/integrations/).

Here are some of the key integrations that PR Pilot supports:

## Github
[GitHub](https://www.github.com) integration is at the core of PR Pilot.
It allows PR Pilot to interact with your repositories, issues and pull requests.

### 🔍 Searching for Issues and PRs
Finding information in Github issues and PRs can be time-consuming, especially when you have a large number of them. PR Pilot can help you search for specific issues or pull requests based on keywords, labels, or other criteria:

```shell
prompt="Find all issues labeled 'critical', read them and summarize them."
pilot task -o critical_issues.md $prompt
```

### 📝 Creating New Issues and PRs
Creating new issues and pull requests in Github can be a tedious process, especially when you have to provide detailed information and assign the right labels. 
Now, you can create new issues in seconds without leaving your editor or terminal:

```shell
pilot task "The AwesomeClass implementation needs refactoring. Read the code and create a new issue with the necessary details."
```

### 🧠 Deep Context Awareness
You can also interact with PR Pilot directly from your Github issues and pull requests. 
By saying `pilot <prompt>` in a comment, you can trigger a task and get the results right in the Github interface.

For example, you can comment on code changes in a PR and ask for adjustments:

![First pilot command](img/first_command.png)
 
To give you the best results, PR Pilot uses the context of the issue or pull request to understand what you need:
- The title and description of the issue or pull request
- Any comments made 
- The files changed in the pull request


## Slack
For many development teams, [Slack](https://www.slack.com) is the central hub of communication.
This provides a number of challenges:

- **Context Switching**: Developers need to switch between Slack and their development environment to get information or perform actions.
- **Lost Information**: Important discussions and decisions can get lost in the noise of Slack channels.
- **Manual Updates**: Keeping team members informed about project updates and changes can be time-consuming.

PR Pilot can help address these challenges by interacting with Slack for you. Connecting PR Pilot to your Slack workspace 
adds new capabilities to its arsenal that you can use in your prompts:

### 🔍 Searching for Slack Messages

Instantly search for specific keywords or messages in your Slack channels and correlate them
with your code or issues.

```shell
pilot task "Search for bug-related messages on Slack, then find related issues on GitHub and Linear"
```

### 💬 Posting Messages to Slack
A common pattern is to use dedicated channels for specific topics or projects, e.g.:
* `#monitoring` for monitoring and alerts
* `#releases` for release announcements
* `#bugs` for bug reports

Enabling the Slack integration allows PR Pilot to relay information to the right channels:

```shell
# Run this as a cron job to post daily bug reports to the #bugs-daily channel
REPOS=("my-org/backend" "my-org/frontend")
PROMPT="Find all 'bug' issues created yesterday, summarize and post them to #bugs-daily on Slack."
for repo in "${REPOS[@]}"; do
  pilot --repo=$repo task $PROMPT
done
```

## Linear
[Linear](https://linear.app/) is a modern issue tracking tool that helps development teams manage their projects efficiently. By integrating PR Pilot with Linear, you can automate various tasks related to issue management, project tracking, and team collaboration.

### 🔍 Searching your Workspace
Linear provides a powerful search functionality that allows you to find specific issues, comments, or projects quickly. By connecting PR Pilot to Linear, you can leverage this search capability in your prompts:

```shell
pilot task "Find all comments made on Linear for team PR Pilot in the last 24 hours. Summarize and send them to #daily on Slack."
```

### 📝 Creating New Issues
Creating new issues in Linear can be a time-consuming task, especially when you have to provide detailed information and assign the right labels. PR Pilot can automate this process by generating new issues based on specific prompts:

```shell
prompt="People have understanding the new ProblemSolver class I wrote. \
1. Find the class in our code and read it \
2. Search slack for messages mentioning the class \
3. Create a Linear issue for documenting the class\nThe issue should include a summary of the class, the messages from slack, and a link to the code."
pilot task $prompt
```
Benefits:
- **Stay in the flow**: No need to switch between tools to gather information
- **Save time**: PR Pilot finds, compiles, formats and posts the information for you
- **Control**: Customize the prompt with more specific requirements and instructions to get the results you need


## Sentry
[Sentry](https://sentry.io) is a popular error tracking tool that helps developers monitor and fix crashes in real-time. By integrating PR Pilot with Sentry, you can automate various tasks related to error tracking, bug analysis, and reporting.

### 🐛 Bug Analysis
Pull together information from different services and tools to analyze bugs with ease.

```shell
pilot task "Look at bug issue #324, find the relevant Sentry events add them as a comment to the issue."
```

### 📊 Reporting
Include stack traces in your [reports](https://github.com/PR-Pilot-AI/demo/tree/main/daily-report).

```shell
pilot task -o report.md "Find new Sentry issues opened yesterday, read the relevant code and write an analysis."
```

### 🏷️ Enrich Tickets
Correlate Sentry events with bug issues on your favorite issue tracker.

```shell
pilot task "Read JIR-324, find the relevant code, correlate it with open Sentry issues and add a comment to the ticket."
```


## CircleCI (coming soon)
[CircleCI](https://circleci.com) integration is coming soon. This will open up a world of powerful new use cases for you, for example:

### ⚡ Quick Access
No more clicking through dashboards. Just ask:

```shell
pilot task "Why did my deployment fail?"
```

### 📊 Reporting
Include insights from pipelines in your [reports](https://github.com/PR-Pilot-AI/demo/tree/main/daily-report).

```shell
pilot task "Generate a report of the last 5 pipeline runs and include insights."
```

### 🐛 Faster Debugging
Quickly correlate build results with code changes and issues.

```shell
pilot task "Look at PR #174, find the related CircleCI build and tell me why it failed."
```

The CircleCI integration will add the following capabilities to PR Pilot:
- Read pipelines and jobs
- Access project insights

## JIRA (coming soon)
[JIRA](https://www.atlassian.com/software/jira) integration is coming soon. This will open up a world of powerful new use cases for you, for example:

### 🔍 Easy Search
Finding stuff in JIRA can be hard. PR Pilot will search and find for you.

```shell
pilot task "Find all 'API' related issues in JIRA opened in the last 7 days."
```

### 🛠️ Assisted Refinements
PR Pilot can read your ticket, find relevant information/code and assist you in adding technical context.

```shell
pilot task "Read JIRA-324, find the related code and add relevant technical context to the ticket."
```

### 🏷️ Format & Label
Let PR Pilot apply your team's style and labeling guidelines to your tickets.

```shell
pilot task "JIRA-324 is messy. Clean it up and apply labels according to our guidelines."
```

The JIRA integration will add the following capabilities to PR Pilot:
- Read and write issues
- Search projects

## Logstash (coming soon)
[Logstash](https://www.elastic.co/logstash) integration is coming soon. This will open up a world of powerful new use cases for you, for example:

### 🐛 Powerful Debugging
With access to bug tickets and your code, PR Pilot will quickly find the right query and fetch the logs for you in seconds.

```shell
pilot task "Look at the bug issue #324 and fetch the logs for the timestamp when the error occurred.
```

### 📈 Prompt-Based Monitoring
Browsing through logs in the browser is annoying. Now you can ask a simple question:

```shell
pilot task "Just had an error on staging. Find the API stacktrace, read the code and tell me what went wrong."
```

### 📊 Kibana Dashboard Generation
Generate custom, use-case specific Kibana dashboards in an instant.

```shell
pilot task "Generate a Kibana dashboard for API error rates in the last 24 hours."
```

The Logstash integration will add the following capabilities to PR Pilot:
- Run Logstash queries
