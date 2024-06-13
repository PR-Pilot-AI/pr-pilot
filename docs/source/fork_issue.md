# Fork Issue Feature

## Overview

The `fork_issue` feature in PR Pilot allows users to copy an issue from the original repository into a forked repository. This tool not only copies the issue but also distills the existing discussion into only the most relevant content, adding it as a comment to the issue in the forked repo. This ensures that developers working on the fork have all the necessary context to address the issue effectively.

## Purpose

The `fork_issue` feature is designed to enhance collaboration on open-source projects by providing a seamless way to transfer issues and their essential context to forked repositories. This is particularly useful for developers who are working on a fork and need to stay updated with the original issue's discussion.

## Benefits

- **Efficient Collaboration**: Ensures that all relevant information is available in the forked repository, facilitating better collaboration.
- **Context Preservation**: Distills and transfers only the most relevant discussion points, avoiding information overload.
- **Seamless Integration**: Integrates smoothly with PR Pilot's existing tools and workflows.

## How to Use the `fork_issue` Tool

### Prerequisites

- Ensure that PR Pilot is installed in both the original and forked repositories.
- The user must have the necessary permissions to create issues in the forked repository.

### Step-by-Step Instructions

1. **Navigate to the Issue**: Go to the issue in the original repository that you want to fork.
2. **Use the `fork_issue` Command**: In the issue comments, type the command `/pilot fork_issue`.
3. **Specify the Forked Repository**: PR Pilot will prompt you to specify the forked repository where the issue should be copied.
4. **Confirm the Action**: Confirm the action, and PR Pilot will handle the rest.

### Example

Suppose you have an issue in the original repository `owner/repo` and you want to fork it to `your-fork/repo`.

1. Go to the issue in `owner/repo`.
2. In the comments, type `/pilot fork_issue`.
3. When prompted, specify `your-fork/repo`.
4. Confirm the action.

PR Pilot will copy the issue to `your-fork/repo` and add a distilled version of the discussion as a comment.

## Considerations

- **Permissions**: Ensure you have the necessary permissions in the forked repository.
- **Relevance**: The tool distills the discussion to the most relevant points, so some less critical comments may not be included.

## Conclusion

The `fork_issue` feature is a powerful tool for developers working on forked repositories, ensuring they have all the necessary context to address issues effectively. By following the steps outlined above, you can easily leverage this feature to enhance your collaboration on open-source projects.
