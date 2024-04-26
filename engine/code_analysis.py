import json
import logging
import subprocess

from django.conf import settings

logger = logging.getLogger(__name__)


def run_semgrep(search_path: str, config="p/r2c"):
    # Define the Semgrep command
    command = [
        "semgrep",
        "--config=" + config,
        "--json",  # Output the results in JSON format
        search_path,
    ]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def json_to_markdown(json_data):
    findings = json.loads(json_data)
    logger.info("Generating Semgrep report")
    markdown_lines = ["# Report\n"]

    results = findings.get("results", [])
    errors = findings.get("errors", [])
    if not results and not errors:
        logger.info("No issues found")
        return "No issues found"

    for result in results:

        rule_id = result.get("check_id")
        path = result.get("path").replace(str(settings.REPO_DIR), "").lstrip("/")
        start_line = result.get("start", {}).get("line")
        message = result.get("extra", {}).get("message")
        logger.info(f"Found issue: {message} in {path}:{start_line}")
        markdown_lines.append(f"## Rule ID: {rule_id}\n")
        markdown_lines.append(f"- **Message**: {message}\n")
        markdown_lines.append(f"- **Path**: {path}:{start_line}\n")
        markdown_lines.append("\n")  # Add an empty line for spacing
    markdown_lines.append("\n\n")  # Add an empty line for spacing
    for error in errors:
        message = error.get("message").replace(str(settings.REPO_DIR), "").lstrip("/")
        logger.info(f"[{error['level']}] {message}")
        markdown_lines.append(f"[{error['level']}] {message}")

    return "\n".join(markdown_lines).strip()


def generate_semgrep_report(semgrep_config="p/python"):
    semgrep_output = run_semgrep(settings.REPO_DIR, semgrep_config)
    markdown_report = json_to_markdown(semgrep_output)
    return markdown_report
