import logging
from typing import List

from django.conf import settings
from github import GithubException
from github.PullRequest import PullRequest
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate, PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from engine.langchain.cost_tracking import CostTrackerCallback
from engine.models import TaskEvent, Task

logger = logging.getLogger(__name__)



system_message = """
You are GithubAgent. You handle interactions with Github.
You will receive a Github-related request and will use your functions to interact with Github.
Do so autonomously and provide the result, without asking for further input.
If you cannot complete the request, abort and provide a reason.
When mentioning Github issues, provide a Markdown-link with number and title.
"""

@tool
def talk_to_github_agent(prompt: str):
    """Talk to the Github agent."""
    TaskEvent.add(actor="Darwin", action="talk_to", target="Github Agent", message=prompt, transaction="begin")
    github_agent = create_github_agent()
    response = github_agent.invoke({"input": prompt})
    TaskEvent.add(actor="Darwin", action="talk_to", target="Github Agent", message=response['output'], transaction="end")
    return response['output']


@tool
def comment_on_github_issue(issue_number: int, comment: str):
    """Comment on a Github issue/PR."""
    g = Task.current().github
    repo = g.get_repo(Task.current().github_project)
    issue = repo.get_issue(issue_number)
    comment = issue.create_comment(comment)
    TaskEvent.add(actor="assistant", action="add_github_comment", target=issue.title,
                       message=f"Commented on [Issue {issue.number}]({comment.html_url})")
    return f"Comment added successfully to issue {issue_number} : {comment.html_url}"

def render_github_issue(issue):
    is_pr = hasattr(issue, 'pull_request') or isinstance(issue, PullRequest)
    return (f"# [{issue.number}] {issue.title}\n"
            f"{issue.html_url}\n"
            f"Created: {issue.created_at}\n"
            f"Labels: {issue.labels}\n"
            f"Is PR: {is_pr}\n")


@tool
def list_open_github_issues():
    """List open issues on Github."""
    g = Task.current().github
    repo = g.get_repo(Task.current().github_project)
    open_issues = repo.get_issues(state='open')
    open_issues = [issue for issue in open_issues if not issue.pull_request]
    if not open_issues:
        return "No open issues found"
    return "\n".join([render_github_issue(issue) for issue in open_issues])


@tool
def list_open_pull_requests():
    """List open pull requests on Github."""
    g = Task.current().github
    repo = g.get_repo(Task.current().github_project)
    open_prs = repo.get_pulls(state='open')
    if not open_prs:
        return "No open pull requests found"
    return "\n".join([render_github_issue(pr) for pr in open_prs])


@tool
def read_pull_request(pr_number: int):
    """Read the pull request and return description + comments + code changes as markdown"""
    # Initialize GitHub client
    g = Task.current().github
    repo = g.get_repo(Task.current().github_project)
    pr: PullRequest = repo.get_pull(pr_number)

    if not pr:
        TaskEvent.add(actor="assistant", action="read_pull_request", message=f"Pull request #{pr_number} not found")
        return f"Pull request #{pr_number} not found"

    TaskEvent.add(actor="assistant", action="read_pull_request", target=str(pr.number), message=f"Reading pull request [{pr.title}]({pr.html_url})")
    labels = ','.join([label.name for label in pr.labels])

    markdown_output = f"# [{pr.number}] {pr.title}\n"
    markdown_output += f"Labels: {labels}\n\n"
    markdown_output += f"## PR Body\n{pr.body}\n\n"

    markdown_output += "## Code Changes\n"
    for file in pr.get_files():
        markdown_output += f"**{file.filename}**\n```diff\n{file.patch}\n```\n\n"

    markdown_output += f"## Review Comments\n"
    # Collect all review comments and properly format them together with the relevant diff_hunk based on in_reply_to_id
    review_comments = list(pr.get_review_comments())
    review_comments.sort(key=lambda x: x.created_at)
    for comment in review_comments:
        if comment.in_reply_to_id:
            # Find the comment that this comment is replying to
            parent_comment = next((c for c in review_comments if c.id == comment.in_reply_to_id), None)
            if parent_comment:
                markdown_output += f"**@{comment.user.login} replied to @{parent_comment.user.login}**\n{comment.body}\n\n"
        else:
            markdown_output += f"**@{comment.user.login} commented on diff:**\n```diff\n{comment.diff_hunk}\n```\n{comment.body}\n\n"

    markdown_output += f"## Issue Comments\n"
    for comment in pr.get_issue_comments():
        markdown_output += f"**@{comment.user.login} wrote:**\n{comment.body}\n\n"

    markdown_output += f"## PR Commits\n"
    for commit in pr.get_commits():
        markdown_output += f"**{commit.commit.author.name}**\n{commit.commit.message}\n\n"


    return markdown_output


@tool
def create_github_issue(issue_title: str, issue_body: str, labels: List[str] = []):
    """Create a new issue on Github. Provide a fitting title, a detailed description and optional one-word, lowercase, alphanumeric labels."""
    g = Task.current().github
    if 'pr-pilot' not in labels:
        labels.append('pr-pilot')
    repo = g.get_repo(Task.current().github_project)
    issue = repo.create_issue(title=issue_title, body=issue_body, labels=labels)
    TaskEvent.add(actor="assistant", action="create_github_issue", target=issue.number, message=f"Created issue [#{issue.number} {issue.title}]({issue.html_url})")
    return f"Created issue [#{issue.number} {issue.title}]({issue.html_url})"


@tool
def edit_github_issue(issue_number: int, new_title: str, new_body: str, labels: List[str] = []):
    """Edit the title, labels and body of a Github issue."""
    g = Task.current().github
    repo = g.get_repo(Task.current().github_project)
    try:
        issue = repo.get_issue(issue_number)
    except GithubException as e:
        if e.status == 404:
            return f"Issue #{issue_number} not found in project {Task.current().github_project}"
        else:
            raise
    issue.edit(title=new_title, body=new_body, labels=labels)
    TaskEvent.add(actor="assistant", action="edit_github_issue", target=issue.number, message=f"Edited issue [#{issue_number} {issue.title}]({issue.html_url})")
    return f"Edited issue [#{issue_number} {new_title}]({issue.html_url})"


@tool
def read_github_issue(issue_number: int):
    """Read the issue and return description + comments as markdown"""
    # Initialize GitHub client
    g = Task.current().github
    repo = g.get_repo(Task.current().github_project)
    issue = repo.get_issue(issue_number)
    labels = ','.join([label.name for label in issue.labels])
    TaskEvent.add(actor="assistant", action="read_github_issue", target=issue.number, message=f"Reading issue [#{issue_number}]({issue.html_url})")
    # Prepare the markdown string
    markdown_output = f"# Issue [{issue.number}] {issue.title}"
    markdown_output += f"## Labels\n{labels}\n\n"
    markdown_output += f"## Body\n{issue.body}\n\n## Comments\n"
    for comment in issue.get_comments():
        markdown_output += f"**{comment.user.login} wrote:**\n{comment.body}\n\n"

    return markdown_output


def create_github_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, callbacks=[CostTrackerCallback("gpt-3.5-turbo", "Github Interaction")])
    tools = [list_open_github_issues, list_open_pull_requests, read_pull_request, read_github_issue, create_github_issue]

    prompt = ChatPromptTemplate.from_messages(
        [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=system_message)),
         HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')),
         MessagesPlaceholder(variable_name='agent_scratchpad')]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=settings.DEBUG)

