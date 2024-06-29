import logging

from django.conf import settings
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from engine.langchain.cost_tracking import CostTrackerCallback
from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


@tool
def talk_to_web_search_agent(prompt: str):
    """Talk to the WebSearch agent."""
    TaskEvent.add(
        actor="Darwin",
        action="talk_to",
        target="Web Searcher",
        message=prompt,
        transaction="begin",
    )
    task_agent = create_web_search_agent()
    response = task_agent.invoke({"input": prompt})
    TaskEvent.add(
        actor="Darwin",
        action="talk_to",
        target="Web Searcher",
        message=response["output"],
        transaction="end",
    )
    return response["output"]


@tool
def scrape_website(url: str):
    """Scrape a website."""
    TaskEvent.add(actor="Darwin", action="scrape", target=url, transaction="begin")
    urls = [url]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    if docs_transformed and docs_transformed[0].page_content:
        return docs_transformed[0].page_content[0:700]
    else:
        logger.error("No content found for URL: %s", url)
        return ""


system_message = """
You are WebSearchAgent. You handle requests to search the web or scrape a specific website.

# How to handle web search requests
- YOU do the research for the user. Instead of returning links, scrape the websites behind the links in order to answer their question
- Do not just return the search results, but use what you found to provide a detailed answer to the question
- Only scrape a website directly if you need to know more about a search result or if you are given a specific URL to scrape
"""


def create_web_search_agent():
    search = TavilySearchResults()
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        callbacks=[CostTrackerCallback("gpt-3.5-turbo", "Web Search")],
    )
    tools = [search, scrape_website]
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
