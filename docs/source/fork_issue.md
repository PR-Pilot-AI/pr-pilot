# `fork_issue` Feature Documentation

## Feature Description

The `fork_issue` tool is a new addition to PR Pilot that allows for the copying of an issue from the original repository into a forked repository. This tool not only copies the issue but also distills the existing discussion into only the most relevant content, adding it as a comment to the issue in the forked repo. This ensures that developers working on the fork have all the necessary context to address the issue effectively.

## Purpose

To provide clear and comprehensive documentation for the `fork_issue` feature, enabling users to understand its functionality, how to use it, and its benefits.

## Target Audience

PR Pilot users, especially those involved in open-source projects who wish to collaborate more effectively on forked repositories.

## Benefits

- **Enhanced Collaboration**: Ensures that all relevant information is available in the forked repository, facilitating better collaboration.
- **Efficiency**: Saves time by distilling discussions to the most relevant points.
- **Context Preservation**: Maintains the context of the original issue, making it easier for developers to understand and address the issue.

## Step-by-Step Instructions

1. **Navigate to the Issue**: Go to the issue you want to fork in the original repository.
2. **Use the `fork_issue` Tool**: Trigger the `fork_issue` tool via the PR Pilot interface or command.
3. **Review the Forked Issue**: Once the issue is forked, review the distilled discussion added as a comment to ensure all necessary context is preserved.

## Prerequisites and Considerations

- Ensure you have the necessary permissions to fork the repository and create issues in the forked repository.
- The `fork_issue` tool relies on PR Pilot's ability to distill discussions, so the quality of the distilled content may vary based on the complexity of the discussion.

## Examples

### Example 1: Forking a Bug Report

1. Original Issue: A bug report with a lengthy discussion on potential fixes.
2. Forked Issue: The `fork_issue` tool copies the bug report to the forked repository and adds a comment summarizing the key points of the discussion, including proposed fixes.

### Example 2: Forking a Feature Request

1. Original Issue: A feature request with various suggestions and feedback.
2. Forked Issue: The `fork_issue` tool copies the feature request to the forked repository and adds a comment summarizing the main suggestions and feedback.

## Conclusion

The `fork_issue` feature is a powerful tool for enhancing collaboration on open-source projects by ensuring that all relevant information is available in forked repositories. By following the steps outlined in this documentation, users can effectively leverage this feature to improve their workflow and collaboration efforts.