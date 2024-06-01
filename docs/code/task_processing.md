# Task Processing in PR Pilot

The lifecycle of a task within PR Pilot involves several key components: `TaskEngine`, `TaskScheduler`, and `TaskWorker`.

## Domain Model



Based on the provided files, here is the Mermaid class diagram illustrating the domain model of the task processing in PR Pilot:

```mermaid
classDiagram
    class TaskEngine {
        -Task task
        -int max_steps
        -executor
        -str github_token
        -Github github
        -Repo github_repo
        -Project project
        +create_unique_branch_name(basis: str) str
        +setup_working_branch(branch_name_basis: str) str
        +finalize_working_branch(branch_name: str) bool
        +generate_task_title()
        +run() str
        +create_bill()
        +clone_github_repo()
    }

    class TaskScheduler {
        -Task task
        -context
        -redis_queue
        +user_budget_empty() bool
        +user_can_write() bool
        +project_has_reached_rate_limit() bool
        +schedule()
    }

    class TaskWorker {
        -redis_queue
        +run()
    }

    class Task {
        <<abstract>>
        -id
        -str github_user
        -str github_project
        -str status
        -str user_request
        -str result
        -str title
        -int pr_number
        -int issue_number
        -context
        +save()
        +objects.get(id: str) Task
    }

    TaskEngine --> Task
    TaskScheduler --> Task
    TaskWorker --> Task
    TaskEngine --> Project
    TaskEngine --> Github
    TaskEngine --> Repo
```

### Description
The task processing in PR Pilot involves three main classes: `TaskEngine`, `TaskScheduler`, and `TaskWorker`.

1. **TaskEngine**: This class is responsible for executing the tasks. It handles the setup of the working branch, finalizes the branch, generates task titles, runs the task, creates bills, and clones the GitHub repository. It interacts with the `Task`, `Project`, `Github`, and `Repo` classes.

2. **TaskScheduler**: This class schedules tasks for execution. It checks if the user has enough budget, if the user has write access to the repository, and if the project has reached its rate limit. Depending on the job strategy, it either runs the task in a background thread, a Kubernetes job, logs the task, or schedules it via Redis.

3. **TaskWorker**: This class continuously listens for tasks in the Redis queue and processes them using the `TaskEngine`.

4. **Task**: This is an abstract representation of a task. It contains attributes like `id`, `github_user`, `github_project`, `status`, `user_request`, `result`, `title`, `pr_number`, `issue_number`, and `context`. It also has methods to save the task and retrieve a task by its ID.

The `TaskEngine`, `TaskScheduler`, and `TaskWorker` classes all interact with the `Task` class to perform their respective functions.

## Task Lifecycle



### Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant TaskScheduler
    participant TaskWorker
    participant TaskEngine
    participant GitHub

    User->>TaskScheduler: Request Task Execution
    TaskScheduler->>TaskScheduler: Validate User Budget
    TaskScheduler->>TaskScheduler: Check User Permissions
    TaskScheduler->>TaskScheduler: Check Rate Limits
    TaskScheduler->>TaskWorker: Schedule Task
    TaskWorker->>TaskWorker: Fetch Task from Queue
    TaskWorker->>TaskEngine: Initialize TaskEngine
    TaskEngine->>GitHub: Clone Repository
    TaskEngine->>TaskEngine: Setup Working Branch
    TaskEngine->>TaskEngine: Execute Task
    TaskEngine->>GitHub: Push Changes
    TaskEngine->>GitHub: Create Pull Request
    TaskEngine->>TaskEngine: Finalize Task
    TaskEngine->>TaskWorker: Task Completed
    TaskWorker->>User: Notify Task Completion
```

### Description

1. **User Request**: The user initiates a task execution request.
2. **TaskScheduler**:
   - Validates the user's budget.
   - Checks if the user has the necessary permissions.
   - Ensures the project has not reached its rate limit.
   - Schedules the task for execution.
3. **TaskWorker**:
   - Fetches the task from the queue.
   - Initializes the `TaskEngine` to handle the task.
4. **TaskEngine**:
   - Clones the GitHub repository.
   - Sets up a working branch.
   - Executes the task using the provided user request.
   - Pushes any changes to the repository.
   - Creates a pull request if necessary.
   - Finalizes the task and updates its status.
5. **Completion**:
   - The `TaskWorker` notifies the user of the task's completion.

This sequence diagram and description illustrate the interaction between the components to execute a task in the PR Pilot system.
