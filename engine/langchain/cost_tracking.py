import logging
import threading
from contextlib import contextmanager
from typing import Any, Generator

import tiktoken
from langchain_community.callbacks.manager import openai_callback_var
from langchain_community.callbacks.openai_info import standardize_model_name, MODEL_COST_PER_1K_TOKENS, \
    get_openai_token_cost_for_model, OpenAICallbackHandler
from langchain_core.outputs import LLMResult

from engine.models.cost_item import CostItem
from engine.models.task import Task

logger = logging.getLogger(__name__)


class CostTrackerCallback(OpenAICallbackHandler):

    def __init__(self, model_name: str, cost_item: str) -> None:
        super().__init__()
        self.model_name = model_name
        self.cost_item = cost_item
        self._lock = threading.Lock()

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        **kwargs: Any,
    ) -> None:
        encoding = tiktoken.get_encoding("cl100k_base")
        prompts_string = ''.join(prompts)
        self.prompt_tokens = len(encoding.encode(prompts_string))

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        message = response.generations[0][0].message
        text_response = response.generations[0][0].text
        cost_item = self.cost_item
        if 'function_call' in message.additional_kwargs:
            text_response = message.additional_kwargs['function_call']['arguments']
            cost_item = message.additional_kwargs['function_call']['name']
        encoding = tiktoken.get_encoding("cl100k_base")
        self.completion_tokens = len(encoding.encode(text_response))
        model_name = standardize_model_name(self.model_name)
        if model_name in MODEL_COST_PER_1K_TOKENS:
            completion_cost = get_openai_token_cost_for_model(
                model_name, self.completion_tokens, is_completion=True
            )
            prompt_cost = get_openai_token_cost_for_model(model_name, self.prompt_tokens)
        else:
            completion_cost = 0
            prompt_cost = 0

        # update shared state behind lock
        with self._lock:
            self.total_cost += prompt_cost + completion_cost
            self.total_tokens = self.prompt_tokens + self.completion_tokens
            self.successful_requests += 1
            CostItem.objects.create(title=cost_item, total_cost_usd=self.total_cost,
                                    requests=self.successful_requests,
                                    completion_token_count=self.completion_tokens,
                                    model_name=self.model_name,
                                    prompt_token_count=self.prompt_tokens,
                                    task=Task.current())
            logger.info(f"Recording cost item for {cost_item} [prompt_tokens={self.prompt_tokens}, completion_tokens={self.completion_tokens}, cost=${self.total_cost}]")
            self.prompt_tokens = 0
            self.total_cost = 0
            self.total_tokens = 0
            self.successful_requests = 0


@contextmanager
def get_cost_tracker_callback(model_name) -> Generator[CostTrackerCallback, None, None]:
    cb = CostTrackerCallback(model_name)
    openai_callback_var.set(cb)
    yield cb
    openai_callback_var.set(None)
