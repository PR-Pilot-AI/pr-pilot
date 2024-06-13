# `fork_issue` Feature Documentation

## Feature Description

The `fork_issue` tool is a new addition to PR Pilot that allows for the copying of an issue from the original repository into a forked repository. This tool not only copies the issue but also distills the existing discussion into only the most relevant content, adding it as a comment to the issue in the forked repo. This ensures that developers working on the fork have all the necessary context to address the issue effectively.

## Purpose

The `fork_issue` feature is designed to enhance collaboration on open-source projects by providing a streamlined way to transfer issues and their essential context to forked repositories.

## Benefits

- **Efficient Collaboration**: Ensures that developers working on forks have all necessary information.
- **Context Preservation**: Distills and transfers only the most relevant discussion points.
- **Ease of Use**: Simplifies the process of copying issues to forked repositories.

## How to Use the `fork_issue` Tool

### Prerequisites

- Ensure you have the necessary permissions to create issues in the forked repository.
- The original repository and the forked repository must be linked.

### Step-by-Step Instructions

1. **Navigate to the Issue**: Go to the issue in the original repository that you want to fork.
2. **Invoke the `fork_issue` Command**: Use the PR Pilot interface to invoke the `fork_issue` command. This can typically be done by commenting on the issue with a specific command recognized by PR Pilot.
3. **Review the Forked Issue**: Once the issue is forked, navigate to the forked repository and review the newly created issue. Ensure that the distilled discussion provides the necessary context.

### Example

Suppose you have an issue in the original repository that needs to be addressed in a fork. By using the `fork_issue` tool, you can seamlessly copy this issue to the fork, along with a distilled version of the discussion, ensuring that the developers working on the fork have all the relevant information.

## Considerations

- **Permissions**: Ensure you have the appropriate permissions in both the original and forked repositories.
- **Relevance of Discussion**: The tool distills the discussion to the most relevant points, so some less critical comments may be omitted.

## Conclusion

The `fork_issue` feature is a powerful tool for enhancing collaboration on open-source projects. By providing a streamlined way to transfer issues and their essential context to forked repositories, it ensures that developers can work more efficiently and effectively.
