# `fork_issue` Feature Documentation

## Feature Description

The `fork_issue` tool is a new addition to PR Pilot that allows for the copying of an issue from the original repository into a forked repository. This tool not only copies the issue but also distills the existing discussion into only the most relevant content, adding it as a comment to the issue in the forked repo. This ensures that developers working on the fork have all the necessary context to address the issue effectively.

## Purpose

To provide clear and comprehensive documentation for the `fork_issue` feature, enabling users to understand its functionality, how to use it, and its benefits.

## Target Audience

PR Pilot users, especially those involved in open-source projects who wish to collaborate more effectively on forked repositories.

## How to Use the `fork_issue` Tool

### Prerequisites

- Ensure that you have the necessary permissions to create issues in the forked repository.
- The original repository and the forked repository must be accessible.

### Step-by-Step Instructions

1. **Navigate to the Issue**: Go to the issue in the original repository that you want to fork.
2. **Use the `fork_issue` Command**: In the comments section of the issue, type the command to fork the issue. For example:
   ```
   /fork_issue
   ```
3. **Wait for Confirmation**: PR Pilot will process the command and create a new issue in the forked repository. You will receive a confirmation once the issue has been successfully forked.
4. **Review the Forked Issue**: Navigate to the forked repository and review the newly created issue. The most relevant content from the original discussion will be added as a comment.

## Benefits

- **Enhanced Collaboration**: Facilitates collaboration on forked repositories by providing all necessary context in the forked issue.
- **Efficiency**: Saves time by automatically distilling and copying relevant discussion content.
- **Seamless Integration**: Integrates smoothly with existing PR Pilot functionalities.

## Examples

### Example 1: Forking an Issue for a Bug Fix

Suppose you are working on a forked repository and come across an issue in the original repository that is relevant to your work. By using the `fork_issue` tool, you can easily copy the issue to your forked repository and have all the necessary context to address the bug.

### Example 2: Forking an Issue for a Feature Request

If you are developing a new feature in a forked repository and find a related issue in the original repository, you can use the `fork_issue` tool to bring that issue into your fork. This ensures that you have all the relevant discussion points and can work on the feature request effectively.

## Additional Notes

This documentation is a valuable resource for users looking to leverage the `fork_issue` feature to enhance collaboration on open-source projects.
