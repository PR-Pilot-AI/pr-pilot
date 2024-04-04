# Domain Model

This document outlines the domain model of PR Pilot, providing insights into the purpose and relationships of the models within the system.

## Models
- **GitHubAccount**: Represents a GitHub user account.
- **GitHubAppInstallation**: Represents an installation of the PR Pilot GitHub app on a user account.
- **Task**: Represents a task that PR Pilot performs, such as processing a command from a GitHub comment.
- **TaskEvent**: Represents an event that occurs during the execution of a Task.
- **TaskBill**: Represents the billing information for a Task.
- **CostItem**: Represents a cost item associated with a Task.
- **PilotUser**: Represents a user of the PR Pilot system.
- **UserBudget**: Represents the budget allocated to a PilotUser for using PR Pilot.

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