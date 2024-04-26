import logging
from enum import Enum

from django.conf import settings
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from engine.code_analysis import generate_semgrep_report
from engine.langchain.cost_tracking import CostTrackerCallback
from engine.models import TaskEvent

logger = logging.getLogger(__name__)


system_message = """
You are AnalysisAgent. You analyze the code base for potential issues and provide insights to the user.
You will receive a request and use your tools to analyze the code base and provide insights.
Do not ask for any user input. Handle and respond to requests right away.
"""


@tool
def run_security_scan():
    """Scan the code base for security vulnerabilities."""
    TaskEvent.add(
        actor="assistant",
        action="security_scan",
        message="Running Security scan with semgrep",
    )
    return generate_semgrep_report("p/security-audit")


class Framework(Enum):
    """Supported frameworks for scanning for framework-specific issues"""

    DJANGO = "django"
    FLASK = "flask"


@tool
def scan_for_framework_vulnerabilities(framework: Framework):
    """Scan the code base for framework vulnerabilities."""
    TaskEvent.add(
        actor="assistant",
        action="code_scan",
        message=f"Scanning for {framework.value}-related issues",
    )
    return generate_semgrep_report(f"p/{framework.value}")


class Language(Enum):
    """Supported languages for scanning for language-specific issues"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    PHP = "php"


@tool
def scan_for_language_vulnerabilities(language: Language):
    """Scan the code base for language-specific vulnerabilities."""
    TaskEvent.add(
        actor="assistant",
        action="code_scan",
        message=f"Scanning for {language.value}-related issues",
    )
    return generate_semgrep_report(f"p/{language.value}")


@tool
def talk_to_analysis_agent_agent(prompt: str):
    """Talk to the Analysis agent."""
    TaskEvent.add(
        actor="Darwin",
        action="talk_to",
        target="Analysis Agent",
        message=prompt,
        transaction="begin",
    )
    github_agent = create_analysis_agent()
    response = github_agent.invoke({"input": prompt})
    TaskEvent.add(
        actor="Darwin",
        action="talk_to",
        target="Analysis Agent",
        message=response["output"],
        transaction="end",
    )
    return response["output"]


def create_analysis_agent():
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        callbacks=[CostTrackerCallback("gpt-3.5-turbo", "Code Analysis")],
    )
    tools = [
        run_security_scan,
        scan_for_language_vulnerabilities,
        scan_for_framework_vulnerabilities,
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=[], template=system_message)
            ),
            HumanMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=["input"], template="{input}")
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=settings.DEBUG)
