import logging
from typing import Optional

from django.conf import settings
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class LabelsAndTitle(BaseModel):
    """Labels and title for a pull request"""

    title: str = Field(description="Title of the pull request")
    labels: list[str] = Field(
        description="Labels for the pull request",
        example=["bug", "feature", "security"],
    )


openai_functions = [convert_to_openai_function(LabelsAndTitle)]


system_message = """
You generate labels and title for a pull request based on its description.
Make sure the title has an emoji and the labels are appropriate.

Description: {description}"""
prompt = PromptTemplate(
    template=system_message,
    input_variables=["description"],
)
parser = JsonOutputFunctionsParser()
model = ChatOpenAI(
    model=settings.DEFAULT_GPT_MODEL,
    openai_api_key=settings.OPENAI_API_KEY,
    temperature=0,
)
chain = prompt | model.bind(functions=openai_functions) | parser


def generate_pr_info(pr_description: str) -> Optional[LabelsAndTitle]:
    """Generate a PullRequestInfo object"""
    response = chain.invoke({"description": pr_description})
    try:
        return LabelsAndTitle(**response)
    except Exception as e:
        logger.error("Error generating PR info", exc_info=e)
        return None
