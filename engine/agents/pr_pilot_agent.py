import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional, Union, List, Dict

from django.conf import settings
from github import Github
from github.Issue import Issue
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from engine.agents.github_agent import (
    read_github_issue,
    read_pull_request,
    create_github_issue,
    edit_github_issue,
    comment_on_github_issue,
    add_label_to_issue,
    remove_label_from_issue,
)
from engine.agents.web_search_agent import scrape_website
from engine.file_system import FileSystem
from engine.langchain.cost_tracking import CostTrackerCallback
from engine.models.task import Task
from engine.models.task_event import TaskEvent
from engine.project import Project
from engine.util import replace_string_in_directory_path

logger = logging.getLogger(__name__)


system_message = """
You are PR Pilot, an AI collaborator on the `{github_project}` Github Project.

# Project Description
{project_info}

# Your Purpose
You will receive a user request related to an issue or PR on the project.
Your job is to fulfill the user request autonomously and provide the response.
All issues, PR, files and code you have access to are in the context of the `{github_project}` repository.

# How to handle user requests
- If the user mentions files, you can read them using the `read_files` function
- If the user mentions classes, methods, etc in the code, you can find them using the `search_for_code_snippets` function
- If necessary, search the internet to make sure your answers are accurate
- Keep your answers short and to the point, unless the user asks for a detailed explanation
- If your answer is based on internet research, make sure to mention the source

# How to handle PR review comments
If you receive a comment on a diff hunk, apply those changes directly to the file system.
Never return the code changes in your response.

# How to handle files
- Reading files is EXPENSIVE. Only read the files you really need to solve the task
- When writing files, ALWAYS write the entire file content, do not leave anything out.

# How to handle Github issues and PRs
- When creating a new issue, include a link back to the original issue or PR in the body
- New issue titles should be descriptive, concise and have an emoji at the beginning

"""

template = """
# Hints for you to better understand the project
Current date and time: {current_time}
{pilot_hints}

# User Request
{user_request}
"""


@tool
def delete_file(path: str):
    """Delete a file from the repository."""
    fs = FileSystem()
    if not fs.get_node(Path(path)):
        return f"File not found: `{path}`"
    TaskEvent.add(
        actor="Darwin",
        action="delete_file",
        target=path,
        message=f"Delete file {path}",
    )
    FileSystem().delete_file(path)
    Project.commit_all_changes(f"Deleted file {path}")
    return f"File deleted: `{path}`"


@tool
def copy_file(source: str, destination: str):
    """Copy a file from one location to another."""
    fs = FileSystem()
    if not fs.get_node(Path(source)):
        return f"File not found: `{source}`"
    TaskEvent.add(
        actor="Darwin",
        action="copy_file",
        target=source,
        message=f"Copy file {source} to {destination}",
    )
    FileSystem().copy_file(source, destination)
    Project.commit_all_changes(f"Copied file {source} to {destination}")
    return f"File copied from {source} to {destination}."


@tool
def move_file(source: str, destination: str):
    """Move a file from one location to another."""
    fs = FileSystem()
    if not fs.get_node(Path(source)):
        return f"File not found: `{source}`"
    TaskEvent.add(
        actor="Darwin",
        action="move_file",
        target=source,
        message=f"Move file {source} to {destination}",
    )
    FileSystem().move_file(source, destination)
    Project.commit_all_changes(f"Moved file {source} to {destination}")
    return f"File moved from {source} to {destination}."


@tool
def write_file(
    path: str, complete_entire_file_content: str, commit_message: Optional[str]
):
    """Write content to a file.
    :param path: Path to the file
    :param complete_entire_file_content: Complete content of the file. NEVER use placeholders or partial content.
    :param commit_message: Short commit message for the change
    """
    path = path.lstrip("/")
    file_system = FileSystem()
    TaskEvent.add(
        actor="assistant",
        action="write_file",
        target=path,
        message=f"Write content to `{path}`",
    )
    file_system.save(complete_entire_file_content, Path(path))
    if not commit_message:
        commit_message = f"Update {path}"
    Project.commit_all_changes(commit_message)
    return f"Successfully wrote content to `{path}`"


@tool
def list_directory(path: str):
    """List the contents of a directory."""
    TaskEvent.add(
        actor="assistant",
        action="list_directory",
        target=path,
        message=f"List directory `{path}`",
    )
    path = path.lstrip("/")
    file_system = FileSystem()
    node = file_system.get_node(Path(path))
    if not node:
        TaskEvent.add(
            actor="assistant",
            action="list_directory",
            target=path,
            message=f"Directory not found `{path}`",
        )
        return f"Directory not found: `{path}`"
    directory_content = f"Content of `{path}`:\n\n"
    for child in sorted(node.nodes, key=lambda x: x.path):
        # Replace the root path with an empty string
        clipped_path = str(child.path).replace(str(settings.REPO_DIR), "")
        # Replace the directory path with an empty string, leaving file name untouched
        clipped_path = replace_string_in_directory_path(clipped_path, path, "").lstrip(
            "/"
        )
        directory_content += f"- {clipped_path}\n"

    return directory_content


@tool
def read_files(file_paths: list[str]):
    """Read the content of the given files."""
    if len(file_paths) > settings.MAX_READ_FILES:
        return f"Too many files ({len(file_paths)}) to read. Please limit to {settings.MAX_READ_FILES} files."
    file_system = FileSystem()
    message = "Read files: \n" + ",".join(
        f"`{file_path}`\n" for file_path in file_paths
    )
    TaskEvent.add(actor="assistant", action="read_files", message=message)
    output = ""
    for file_path in file_paths:
        file_path = file_path.lstrip("/")
        file_node = file_system.get_node(Path(file_path))
        if file_node:
            output += f"### {file_path}\n"
            output += file_node.content
            output += "\n\n"
        else:
            output += f"File not found: `{file_path}`\n"
    non_empty_line_count = len([line for line in output.split("\n") if line.strip()])
    if non_empty_line_count > settings.MAX_FILE_LINES:
        return f"The content of {file_paths} is longer than {settings.MAX_FILE_LINES} lines and too expensive to analyze. Abort!"
    return output


@tool
def search_github_code(query: str, sort: Optional[str], order: Optional[str]):
    """Search for code in the repository.
    :param query: Search query in Github search syntax
    :param sort: string ('indexed')
    :param order: string ('asc', 'desc')
    """
    g = Task.current().github
    # Force query to use the repository name
    query = f"repo:{Task.current().github_project} {query}"

    results = g.search_code(query, sort=sort, order=order)
    if not results.totalCount:
        TaskEvent.add(
            actor="assistant",
            action="search_code",
            message=f"Searched code with query: `{query}`. No results.",
        )
        return "No code found"

    response = ""
    relevant_files = ""
    for result in results:
        relevant_files += f"- `{result.path}`\n"
        if result.text_matches:
            for match in result.text_matches:
                response += f"**Match in `{result.path}`**\n"
                response += f"```\n{match['fragment']}\n```\n\n"
        else:
            response += f"**File `{result.path}`**\n"
    TaskEvent.add(
        actor="assistant",
        action="search_code",
        message=f"Searched code with query: `{query}`. Found {results.totalCount} results:\n\n{relevant_files}",
    )
    return response


@tool
def search_for_code_snippets(search_regex: str, glob: str) -> str:
    """
    Search the code base for a specific regex pattern.

    Args:
    - search_regex: Regex pattern used for searching file contents (e.g. 'def function_name', '\b\\w*Controller\b')
    - glob: Glob pattern to limit the search to specific files / directories (e.g., 'src' or '*.{c,h}').

    Returns:
    A list of code snippets and their location in the code base.

    Note:
        - Do NOT use file names in the `search_regex` parameter. Use the `glob` parameter to limit the search to specific files.
    """
    search_path = os.path.join(settings.REPO_DIR, glob)
    command = f"rg -n {shlex.quote(search_regex)} {str(search_path)}"
    TaskEvent.add(
        actor="assistant",
        action="search_code",
        message=f"Searching code for pattern: `{search_regex}` in `{glob}`.",
    )
    try:
        result = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            if not result.stdout:
                return f"No matches found for pattern `{search_regex}` in `{glob}`."
            result = result.stdout.strip()
            root_path_replaced = result.replace(str(settings.REPO_DIR), "")
            max_100_lines = root_path_replaced.split("\n")[:150]
            return "\n".join(max_100_lines)
        else:
            return "An error occurred." + result.stderr
    except Exception as e:
        return f"An error occurred while running ripgrep: {e}"


@tool
def search_github_issues(query: str, sort: Optional[str], order: Optional[str]):
    """Search for issues in the repository.
    :param query: Search query in Github search syntax
    :param sort: string ('created', 'updated', 'comments')
    :param order: string ('asc', 'desc')
    """
    g = Task.current().github
    # Force query to use the repository name
    query = f"{query} repo:{Task.current().github_project}"
    results = g.search_issues(query, sort=sort, order=order)
    if not results.totalCount:
        TaskEvent.add(
            actor="assistant",
            action="search_issues",
            message=f"Search issues with query: `{query}`. No results.",
        )
        return "No issues found"
    response = ""
    for result in results:
        response += f"**Issue #{result.number}**\n"
        response += f"[{result.title}]({result.html_url})\n\n"
    TaskEvent.add(
        actor="assistant",
        action="search_issues",
        message=f"Search issues with query: `{query}`. Found {results.totalCount} results.",
    )
    return response


class PRPilotSearch(TavilySearchResults):

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Union[List[Dict], str]:
        TaskEvent.add(
            actor="assistant", action="search", message=f"Search Internet for `{query}`"
        )
        return super()._run(query, run_manager)


@tool
def fork_issue(github_project: str, issue_number: int):
    """'Forks' a Github issue from an upstream project into our current project.

    Parameters:
    - github_project: The Github project that contains the original issue.
    - issue_number: The number of the issue to be forked.
    """
    task = Task.current()
    original_repo = Github().get_repo(github_project)
    original_issue: Issue = original_repo.get_issue(issue_number)
    title = original_issue.title
    body = original_issue.body
    comments = [
        f"**User {comment.user.id}**:\n{comment.body}\n"
        for comment in original_issue.get_comments()
    ]
    distilled_comments = "\n".join(comments)
    body = (
        f"**This is a copy of {original_issue.html_url}**\n\n---\n\n"
        + body
        + "\n\n---\n# Original Comments\n\n"
        + distilled_comments
    )
    # Create a new issue in the forked repository
    forked_issue = task.github.get_repo(task.github_project).create_issue(
        title=f"Forked: {title}", body=body
    )
    return f"Issue #{issue_number} has been successfully forked to {github_project} as Issue #{forked_issue.number}."


def create_pr_pilot_agent(
    gpt_model=settings.DEFAULT_GPT_MODEL, image_support=False, additional_tools=()
):
    llm = ChatOpenAI(
        model=gpt_model,
        temperature=0,
        callbacks=[CostTrackerCallback(gpt_model, "conversation")],
    )
    tools = [
        comment_on_github_issue,
        add_label_to_issue,
        remove_label_from_issue,
        read_github_issue,
        read_pull_request,
        create_github_issue,
        write_file,
        read_files,
        list_directory,
        search_for_code_snippets,
        search_github_issues,
        edit_github_issue,
        copy_file,
        move_file,
        delete_file,
        PRPilotSearch(),
        scrape_website,
    ] + additional_tools
    primer = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["github_project", "project_info"],
            template=system_message,
        )
    )
    image_message = HumanMessagePromptTemplate.from_template(
        template=[
            {
                "type": "image_url",
                "image_url": "{encoded_image_url}",
            }
        ]
    )
    user_request = HumanMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=["user_request"], template=template)
    )
    scratchpad = MessagesPlaceholder(variable_name="agent_scratchpad")
    final_system_message = SystemMessage(
        "Fulfill the user request autonomously and respond to them, "
        "without asking for further input. If anything fails along the way, abort and provide a reason."
    )
    all_messages = [
        primer,
        user_request,
        scratchpad,
        final_system_message,
    ]
    if image_support:
        all_messages.insert(1, image_message)
    prompt = ChatPromptTemplate.from_messages(all_messages)
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, tools=tools, verbose=settings.DEBUG, handle_parsing_errors=True
    )
