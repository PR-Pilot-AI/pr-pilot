# Task Processing in PR Pilot

The lifecycle of a task within PR Pilot involves several key components: `TaskEngine`, `TaskScheduler`, and `TaskWorker`.

## Domain Model

```mermaid
classDiagram
    class TaskEngine {
        -Task task
        -int max_steps
        -Executor executor
        -str github_token
        -Github github
        -Repository github_repo
        -Project project
        +__init__(task: Task, max_steps=5)
        +create_unique_branch_name(basis: str)
        +setup_working_branch(branch_name_basis: str)
        +finalize_working_branch(branch_name: str) bool
        +generate_task_title()
        +run() str
        +create_bill()
        +clone_github_repo()
    }

    class TaskScheduler {
        -Task task
        -Context context
        -Redis redis_queue
        +__init__(task)
        +user_budget_empty() bool
        +user_can_write() bool
        +project_has_reached_rate_limit() bool
        +schedule()
    }

    class TaskWorker {
        -Redis redis_queue
        +__init__()
        +run()
    }

    class Task {
        <<ORM Model>>
        -int id
        -str status
        -str result
        -str github_user
        -str github_project
        -str user_request
        -str gpt_model
        -int installation_id
        -int pr_number
        -int issue_number
        -str head
        -Context context
        +save()
    }

    TaskEngine --> Task
    TaskScheduler --> Task
    TaskWorker --> TaskEngine
    TaskWorker --> Task
```

The task processing in PR Pilot involves three main classes: `TaskEngine`, `TaskScheduler`, and `TaskWorker`.

1. **TaskEngine**: This class is responsible for executing the tasks. It initializes with a `Task` object and sets up the environment for task execution. It handles branch creation, task execution, and finalization, including pushing changes and creating pull requests if necessary. It also manages billing and repository cloning.

2. **TaskScheduler**: This class schedules tasks for execution. It checks the user's budget, permissions, and rate limits before scheduling a task. Depending on the job strategy (thread, Kubernetes, log, or Redis), it schedules the task accordingly.

3. **TaskWorker**: This class continuously listens for tasks in the Redis queue and processes them using the `TaskEngine`. It sets up the necessary environment variables and logging context before running the task.

4. **Task**: This is an ORM model representing a task. It contains various attributes related to the task, such as status, result, GitHub user, project, request, and context. It also provides a method to save the task state.

The `TaskEngine` interacts with the `Task` to perform the actual task execution, while the `TaskScheduler` ensures that tasks are scheduled correctly. The `TaskWorker` listens for tasks and uses the `TaskEngine` to process them.

## Task Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant TaskScheduler
    participant TaskWorker
    participant TaskEngine
    participant GitHub

    User->>TaskScheduler: Request Task Execution
    TaskScheduler->>TaskScheduler: Validate User Budget
    TaskScheduler->>TaskScheduler: Validate User Permissions
    TaskScheduler->>TaskScheduler: Check Rate Limit
    TaskScheduler->>TaskWorker: Schedule Task
    TaskWorker->>TaskWorker: Fetch Task from Queue
    TaskWorker->>TaskEngine: Initialize TaskEngine
    TaskEngine->>GitHub: Clone Repository
    TaskEngine->>TaskEngine: Setup Working Branch
    TaskEngine->>TaskEngine: Execute Task
    TaskEngine->>GitHub: Push Changes
    TaskEngine->>GitHub: Create Pull Request
    TaskEngine->>TaskEngine: Generate Bill
    TaskEngine->>User: Respond with Result
```

1. **User Request**: The user initiates a task execution request.
2. **TaskScheduler**: 
   - Validates the user's budget.
   - Checks if the user has the necessary permissions.
   - Ensures the project has not reached its rate limit.
   - Schedules the task for execution.
3. **TaskWorker**: 
   - Fetches the task from the queue.
   - Initializes the `TaskEngine`.
4. **TaskEngine**: 
   - Clones the GitHub repository.
   - Sets up a working branch.
   - Executes the task using the PR Pilot agent.
   - Pushes any changes to the repository.
   - Creates a pull request if necessary.
   - Generates a bill for the task.
5. **User Response**: The user is informed of the task result, including any pull requests created.
