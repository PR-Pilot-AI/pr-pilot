# Prompt Guide

Writing a good prompt can make the difference between a good and a terrible user experience. This guide provides tips and examples to help you write effective prompts for PR Pilot.

## Tips for Writing Good Prompts

1. **Be Clear and Specific**: Clearly state what you want to achieve. Avoid vague language.
   - **Bad**: "Fix the code."
   - **Good**: "Fix the bug in the `process_data` function where it fails to handle empty input."

2. **Provide Context**: Give enough background information so the AI understands the task.
   - **Bad**: "Add tests."
   - **Good**: "Add unit tests for the `calculate_sum` function to cover edge cases like negative numbers and large inputs."

3. **Use Examples**: When possible, provide examples of the expected output.
   - **Bad**: "Format the output."
   - **Good**: "Format the output as a JSON object with keys `name`, `age`, and `email`."

4. **Be Concise**: While context is important, avoid unnecessary details that might confuse the AI.
   - **Bad**: "In the function that we discussed last week during the meeting, make sure to handle the edge cases we talked about."
   - **Good**: "Ensure the `parse_input` function handles empty strings and null values."

5. **Iterate and Refine**: If the AI's response isn't what you expected, refine your prompt and try again.
   - **First Attempt**: "Generate a report."
   - **Refined**: "Generate a sales report for Q1 2024, including total sales, top-selling products, and sales by region."

## Examples of Good Prompts

- "Create a new Django model named `Product` with fields `name` (char), `price` (decimal), and `stock` (integer)."
- "Optimize the `fetch_data` function to reduce its runtime complexity from O(n^2) to O(n log n)."
- "Write a Dockerfile for a Python application that uses Flask and has a dependency on `requests`."
- "Set up a GitHub Action to run tests on every pull request. Use the `ubuntu-latest` runner and Python 3.8."

By following these guidelines, you can write prompts that help PR Pilot understand your needs and deliver better results.
