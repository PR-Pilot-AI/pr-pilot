# Domain Model

This document outlines the domain model of PR Pilot, providing insights into the purpose and relationships of the models within the system.

## Models
- **GitHubAccount**: Represents a GitHub user account. Defined in `webhooks/models.py`.
- **GitHubAppInstallation**: Represents an installation of the PR Pilot GitHub app on a user account. Defined in `webhooks/models.py`.
- **Task**: Represents a task that PR Pilot performs, such as processing a command from a GitHub comment. Defined in `engine/models.py`.
- **TaskEvent**: Represents an event that occurs during the execution of a Task. Defined in `engine/models.py`.
- **TaskBill**: Represents the billing information for a Task. Defined in `engine/models.py`.
- **CostItem**: Represents a cost item associated with a Task. Defined in `engine/models.py`.
- **PilotUser**: Represents a user of the PR Pilot system. Defined in `accounts/models.py`.
- **UserBudget**: Represents the budget allocated to a PilotUser for using PR Pilot. Defined in `accounts/models.py`.

## Overview
The domain model of PR Pilot revolves around the concept of Tasks. A Task is created whenever a user interacts with PR Pilot by issuing a command through a GitHub comment. Each Task can generate multiple TaskEvents, which track the progress and actions taken during the Task's execution. TaskBills and CostItems are used to manage the billing and cost associated with executing a Task. The GitHubAccount and GitHubAppInstallation models facilitate the interaction between PR Pilot and GitHub, while the PilotUser and UserBudget models manage the users of the PR Pilot system and their allocated budgets.

```mermaid
classDiagram
    GitHubAccount "1" -- "1" GitHubAppInstallation : has
    Task "1" -- "*" TaskEvent : generates
    Task "1" -- "1" TaskBill : billed through
    Task "*" -- "*" CostItem : includes
    PilotUser "1" -- "*" UserBudget : allocates
```

## TaskEngine, Task, and TaskScheduler

This section visualizes the relationship between `TaskEngine`, `Task`, and `TaskScheduler` within the PR Pilot project. `TaskEngine` is responsible for executing tasks, while `TaskScheduler` is responsible for scheduling them. `Task` acts as the central entity that is executed by the `TaskEngine` and scheduled by the `TaskScheduler`.

```mermaid
classDiagram
    class TaskEngine {
        +Task task
        +int max_steps
        +create_unique_branch_name(basis: str): str
        +setup_working_branch(branch_name_basis: str): str
        +finalize_working_branch(branch_name: str): bool
        +generate_task_title(): void
        +run(): str
        +create_bill(): void
        +clone_github_repo(): void
    }
    class Task {
        -UUID id
        -String task_type
        -String title
        -String status
        -DateTime created
        -int installation_id
        -String github_project
        -String github_user
        -String branch
        -int issue_number
        -int pr_number
        -String user_request
        -String head
        -String base
        -int comment_id
        -String comment_url
        -int response_comment_id
        -String response_comment_url
        -String result
        -String pilot_command
        +schedule(): void
    }
    class TaskScheduler {
        +Task task
        +schedule(): void
    }
    TaskEngine --|> Task : executes
    TaskScheduler --|> Task : schedules
```
