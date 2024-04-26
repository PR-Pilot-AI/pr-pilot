import os
import re

from django.core.management import call_command


def slugify(text: str) -> str:
    """Remove special characters from a string."""
    return re.sub(r"[\W_]+", "-", text.lower()).strip("-")


def clean_code_block_with_language_specifier(response):
    lines = response.split("\n")

    # Check if the first line starts with ``` followed by a language specifier and the last line is just ```
    if lines[0].startswith("```") and lines[-1].strip() == "```":
        # Remove the first and last lines
        cleaned_lines = lines[1:-1]
    else:
        cleaned_lines = lines

    clean_response = "\n".join(cleaned_lines)
    return clean_response


def run_task_in_background(task_id):
    call_command("run_task", task_id)


def replace_string_in_directory_path(path, old_dir, new_dir):
    """Replace a directory name in a path with a new directory name, leave the file name untouched."""
    # Split the path into its components
    path_parts = path.split(os.sep)

    # Replace the directory name in the path parts, excluding the last part (filename)
    new_parts = [
        new_dir if part == old_dir and i != len(path_parts) - 1 else part
        for i, part in enumerate(path_parts)
    ]

    # Reconstruct the path from the modified parts
    new_path = os.sep.join(new_parts)
    return new_path
