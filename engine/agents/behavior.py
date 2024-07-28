import logging
from typing import Optional

from django.utils import timezone
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field, create_model
from pydantic.v1.fields import FieldInfo

from accounts.models import PilotUser
from engine.agents.integration_tools import integration_tools_for_user
from engine.util import slugify

MAX_TOOL_NAME_LEN = 35

logger = logging.getLogger(__name__)


def build_agent_behavior_tool_function(task, project_info, pilot_hints, instructions):
    """Build a function that will be used to create a LangChain tool for the agent behavior.
    Args:
        task: Task object
        project_info: Project information
        pilot_hints: Pilot hints
        instructions: Instructions for the agent
        Returns: A function that will be used to create a LangChain tool for the agent behavior
    """

    def agent_behavior_tool_function(**input):

        from engine.agents.pr_pilot_agent import create_pr_pilot_agent

        executor = create_pr_pilot_agent(
            task.gpt_model,
            image_support=False,
            additional_tools=integration_tools_for_user(
                PilotUser.objects.get(username=task.github_user)
            ),
        )

        date_and_time = (
            timezone.now().isoformat() + " " + str(timezone.get_current_timezone())
        )
        input_list = ("\n").join([f"{key}: {value}" for key, value in input.items()])
        user_request = f"{input_list}\n\n---\n\n{instructions}"
        executor_result = executor.invoke(
            {
                "user_request": user_request,
                "github_project": task.github_project,
                "project_info": project_info,
                "pilot_hints": pilot_hints,
                "current_time": date_and_time,
            }
        )
        return executor_result["output"]

    return agent_behavior_tool_function


class AgentBehavior(BaseModel):
    """User-defined behavior for the PR Pilot agent."""

    title: str = Field(..., title="Short title of the behavior")
    args: Optional[dict] = Field(
        None, title="Arguments required to perform the behavior"
    )
    instructions: str = Field(..., title="Instructions for the agent")
    result: Optional[str] = Field(
        "A short summary of your actions", title="Expected result of the behavior"
    )

    @property
    def slug(self):
        return slugify(self.title)[:MAX_TOOL_NAME_LEN].replace("-", "_")

    def to_agent_tool(self, task, project_info, pilot_hints):
        """Convert the user-defined behavior to a LangChain tool."""
        final_instructions = self.instructions
        if self.result:
            final_instructions += f"\n\nRespond with: {self.result}"
        fields = {}
        for key, value in self.args.items():
            fields[key.replace(" ", "-")] = (str, FieldInfo(title=value))
        AgentBehaviorToolSchema = create_model("AgentBehaviorToolSchema", **fields)

        return StructuredTool(
            name=self.slug,
            func=build_agent_behavior_tool_function(
                task, project_info, pilot_hints, self.instructions
            ),
            description=self.title,
            args_schema=AgentBehaviorToolSchema,
        )
