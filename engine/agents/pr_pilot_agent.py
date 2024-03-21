import logging
import shlex
import subprocess
from pathlib import Path
from typing import Optional, Union, List, Dict

from django.conf import settings
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate, PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from engine.agents.common import AGENT_COMMUNICATION_RULES
from engine.agents.github_agent import read_github_issue, read_pull_request, create_github_issue, edit_github_issue
from engine.agents.web_search_agent import scrape_website
from engine.file_system import FileSystem
from engine.langchain.cost_tracking import CostTrackerCallback
from engine.models import TaskEvent, Task
from engine.project import Project

logger = logging.getLogger(__name__)




system_message = """
You are PR Pilot, an AI collaborator on the `{github_project}` Github Project.
You will receive a user request related to an issue or PR on the project.
Your job is to fulfill the user request autonomously and provide the response.
All issues, PR, files and code you have access to are in the context of the `{github_project}` repository.

# How to handle user requests
- If the user mentions classes, methods, etc in the code, you can find them using the `search_with_ripgrep` function
- If necessary, search the internet to make sure your answers are accurate
- Keep your answers short and to the point, unless the user asks for a detailed explanation
- If your answer is based on internet research, make sure to mention the source  

# How to handle files
- Reading files is EXPENSIVE. Only read the files you really need to solve the task
- When writing files, ALWAYS write the entire file content, do not leave anything out.

# How to handle Github issues and PRs
- When creating a new issue, include a link back to the original issue or PR in the body
- New issue titles should be descriptive, concise and have an emoji at the beginning

"""

template = """
# Hints for you to better understand the project
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
    TaskEvent.add(actor="Darwin", action="delete_file", target=path, message=f"Deleting file {path}")
    FileSystem().delete_file(path)
    Project.commit_all_changes(f"Deleted file {path}")
    return f"File deleted: `{path}`"

@tool
def copy_file(source: str, destination: str):
    """Copy a file from one location to another."""
    fs = FileSystem()
    if not fs.get_node(Path(source)):
        return f"File not found: `{source}`"
    TaskEvent.add(actor="Darwin", action="copy_file", target=source, message=f"Copying file {source} to {destination}")
    FileSystem().copy_file(source, destination)
    Project.commit_all_changes(f"Copied file {source} to {destination}")
    return f"File copied from {source} to {destination}."

@tool
def move_file(source: str, destination: str):
    """Move a file from one location to another."""
    fs = FileSystem()
    if not fs.get_node(Path(source)):
        return f"File not found: `{source}`"
    TaskEvent.add(actor="Darwin", action="move_file", target=source, message=f"Moving file {source} to {destination}")
    FileSystem().move_file(source, destination)
    Project.commit_all_changes(f"Moved file {source} to {destination}")
    return f"File moved from {source} to {destination}."

@tool
def write_file(path: str, complete_entire_file_content: str, commit_message: str):
    """Write content to a file.
    :param path: Path to the file
    :param complete_entire_file_content: Complete content of the file. NEVER use placeholders or partial content.
    :param commit_message: Short commit message for the change
    """
    path = path.lstrip("/")
    file_system = FileSystem()
    TaskEvent.add(actor="assistant", action="write_file", target=path)
    file_system.save(complete_entire_file_content, Path(path))
    Project.commit_all_changes(commit_message)
    return f"Successfully wrote content to `{path}`"


@tool
def read_files(file_paths: list[str]):
    """Read the content of the given files."""
    if len(file_paths) > settings.MAX_READ_FILES:
        return f"Too many files ({len(file_paths)}) to read. Please limit to {settings.MAX_READ_FILES} files."
    file_system = FileSystem()
    message = "Reading files: \n" + "\n- ".join(f"`{file_path}`\n" for file_path in file_paths)
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
        TaskEvent.add(actor="assistant", action="search_code", message=f"Searched code with query: `{query}`. No results.")
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
    TaskEvent.add(actor="assistant", action="search_code", message=f"Searched code with query: `{query}`. Found {results.totalCount} results:\n\n{relevant_files}")
    return response

@tool
def search_with_ripgrep(search_pattern: str, file_type: str = None) -> str:
    """
    Search for a pattern in files using ripgrep.

    Args:
    - search_pattern: The regex pattern to search for.
    - path: The path to search within. Can be a file or a directory.
    - file_type: Optionally, a file type to limit the search to (e.g., 'py' for Python files).

    Returns:
    A list of search results
    """
    command = f"rg -n {shlex.quote(search_pattern)} {shlex.quote(str(settings.REPO_DIR))}"
    if file_type:
        command += f" -t {file_type}"
    TaskEvent.add(actor="assistant", action="search_code", message=f"Searching code for pattern: `{search_pattern}`.")
    try:
        result = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout:
            result = result.stdout.strip()
            root_path_replaced = result.replace(str(settings.REPO_DIR), "")
            max_100_lines = root_path_replaced.split("\n")[:150]
            return "\n".join(max_100_lines)
        else:
            return "No matches found or an error occurred."
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
        TaskEvent.add(actor="assistant", action="search_issues", message=f"Searched issues with query: `{query}`. No results.")
        return "No issues found"
    response = ""
    for result in results:
        response += f"**Issue #{result.number}**\n"
        response += f"[{result.title}]({result.html_url})\n\n"
    TaskEvent.add(actor="assistant", action="search_issues", message=f"Searched issues with query: `{query}`. Found {results.totalCount} results:\n\n{response}")
    return response


class PRPilotSearch(TavilySearchResults):

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Union[List[Dict], str]:
        TaskEvent.add(actor="assistant", action="search", message=query)
        return super()._run(query, run_manager)


def create_pr_pilot_agent():
    llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, callbacks=[CostTrackerCallback("gpt-4-turbo-preview", "conversation")])
    tools = [read_github_issue, read_pull_request, create_github_issue, write_file, read_files, search_with_ripgrep, search_github_issues, edit_github_issue, copy_file, move_file, delete_file, PRPilotSearch(), scrape_website]
    prompt = ChatPromptTemplate.from_messages(
        [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['github_project', 'project_info'], template=system_message)),
         HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['user_request'], template=template)),
         MessagesPlaceholder(variable_name='agent_scratchpad'),
         SystemMessage('Fulfill the user request autonomously and provide the response, without asking for further input. If anything fails along the way, abort and provide a reason.')]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=settings.DEBUG)

