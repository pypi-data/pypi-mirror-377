"""
Real-time evaluation of responses from OpenAI Chat Completions API.

If you are using OpenAI's Chat Completions API, this module allows you to incorporate TLM trust scoring without any change to your existing code.
It works for any OpenAI LLM model, as well as the many other non-OpenAI LLMs that are also usable via Chat Completions API (Gemini, DeepSeek, Llama, etc).
"""

import asyncio
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from cleanlab_tlm.internal.api.api import tlm_chat_completions_score
from cleanlab_tlm.internal.base import BaseTLM
from cleanlab_tlm.internal.constants import (
    _DEFAULT_TLM_QUALITY_PRESET,
    _VALID_TLM_QUALITY_PRESETS,
)
from cleanlab_tlm.internal.types import TLMQualityPreset
from cleanlab_tlm.tlm import TLM, TLMOptions, TLMResponse, TLMScore
from cleanlab_tlm.utils.chat import _form_prompt_chat_completions_api, form_response_string_chat_completions

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion, ChatCompletionMessage


class TLMChatCompletion(BaseTLM):
    """
    Represents a Trustworthy Language Model (TLM) instance specifically designed for evaluating OpenAI Chat Completions responses.

    This class provides a TLM wrapper that can be used to evaluate the quality and trustworthiness of responses from any OpenAI model
    by passing in the inputs to OpenAI's Chat Completions API and the ChatCompletion response object.

    Args:
        quality_preset ({"base", "low", "medium", "high", "best"}, default = "medium"): an optional preset configuration to control
            the quality of TLM trustworthiness scores vs. latency/costs.

        api_key (str, optional): Cleanlab TLM API key. If not provided, will attempt to read from CLEANLAB_API_KEY environment variable.

        options ([TLMOptions](../tlm/#class-tlmoptions), optional): a typed dict of configurations you can optionally specify.
            See detailed documentation under [TLMOptions](../tlm/#class-tlmoptions).

        timeout (float, optional): timeout (in seconds) to apply to each TLM evaluation.
    """

    def __init__(
        self,
        quality_preset: TLMQualityPreset = _DEFAULT_TLM_QUALITY_PRESET,
        *,
        api_key: Optional[str] = None,
        options: Optional[TLMOptions] = None,
        timeout: Optional[float] = None,
    ):
        """
        lazydocs: ignore
        """
        super().__init__(
            quality_preset=quality_preset,
            valid_quality_presets=_VALID_TLM_QUALITY_PRESETS,
            support_custom_eval_criteria=True,
            api_key=api_key,
            options=options,
            timeout=timeout,
            verbose=False,
        )

        self._tlm = TLM(
            quality_preset=quality_preset,
            api_key=api_key,
            options=options,
            timeout=timeout,
        )

    def score(
        self,
        *,
        response: "ChatCompletion",
        **openai_kwargs: Any,
    ) -> TLMScore:
        """Score the trustworthiness of an OpenAI ChatCompletion response.

        Args:
            response (ChatCompletion): The OpenAI ChatCompletion response object to evaluate
            **openai_kwargs (Any): The original kwargs passed to OpenAI's create() method, must include 'messages'

        Returns:
            TLMScore: A dict containing the trustworthiness score and optional logs
        """
        self._validate_chat_completion(response)
        if (messages := openai_kwargs.get("messages")) is None:
            raise ValueError("messages is a required OpenAI input argument.")

        combined_kwargs = {
            "quality_preset": self._quality_preset,
            **openai_kwargs,
            **self._options,
        }

        # handle structured outputs differently
        if openai_kwargs.get("response_format"):
            return cast(
                TLMScore,
                self._event_loop.run_until_complete(
                    asyncio.wait_for(
                        tlm_chat_completions_score(
                            api_key=self._api_key,
                            response=response,
                            **combined_kwargs,
                        ),
                        timeout=self._timeout,
                    )
                ),
            )

        # all other cases
        tools = openai_kwargs.get("tools", None)

        prompt_text = _form_prompt_chat_completions_api(messages, tools)
        response_text = form_response_string_chat_completions(response=response)

        return cast(TLMScore, self._tlm.get_trustworthiness_score(prompt_text, response_text))

    def get_explanation(
        self,
        *,
        response: Optional["ChatCompletion"] = None,
        tlm_result: Union[TLMScore, "ChatCompletion"],
        **openai_kwargs: Any,
    ) -> str:
        """Gets explanations for a given prompt-response pair with a given score.

        This method provides detailed explanations from TLM about why a particular response
        received its trustworthiness score.

        The `tlm_result` object will be mutated to include the explanation in its log.

        Args:
            response (ChatCompletion, optional): The OpenAI ChatCompletion response object to evaluate
            tlm_result (TLMScore | ChatCompletion): The result object from a previous TLM call
            **openai_kwargs (Any): The original kwargs passed to OpenAI's create() method, must include 'messages'

        Returns:
            str: Explanation for why TLM assigned the given trustworthiness score to the response.
        """
        try:
            from openai.types.chat import ChatCompletion
        except ImportError as e:
            raise ImportError(
                f"OpenAI is required to use the {self.__class__.__name__} class. Please install it with `pip install openai`."
            ) from e

        if (messages := openai_kwargs.get("messages")) is None:
            raise ValueError("messages is a required OpenAI input argument.")
        tools = openai_kwargs.get("tools", None)

        prompt_text = _form_prompt_chat_completions_api(messages, tools)

        if isinstance(tlm_result, dict):
            if response is None:
                raise ValueError("'response' is required when tlm_result is a TLMScore object")

            response_text = form_response_string_chat_completions(response=response)
            return cast(
                str,
                self._tlm.get_explanation(
                    prompt=prompt_text,
                    response=response_text,
                    tlm_result=tlm_result,
                ),
            )

        if isinstance(tlm_result, ChatCompletion):
            if getattr(tlm_result, "tlm_metadata", None) is None:
                raise ValueError("tlm_result must contain tlm_metadata.")

            response_text = form_response_string_chat_completions(response=tlm_result)
            tlm_metadata = tlm_result.tlm_metadata  # type: ignore
            formatted_tlm_result = cast(
                TLMResponse,
                {
                    "response": response_text,
                    **tlm_metadata,
                },
            )

            explanation = self._tlm.get_explanation(
                prompt=prompt_text,
                tlm_result=formatted_tlm_result,
            )

            if "log" in tlm_metadata:
                tlm_metadata["log"]["explanation"] = explanation
            else:
                tlm_metadata["log"] = {"explanation": explanation}

            return cast(str, explanation)

        raise TypeError("tlm_result must be a TLMScore or ChatCompletion object.")

    @staticmethod
    def _get_response_message(response: "ChatCompletion") -> "ChatCompletionMessage":
        return response.choices[0].message

    def _validate_chat_completion(self, response: Any) -> None:
        # `response` should be a ChatCompletion, but isinstance checks wouldn't be reachable
        try:
            from openai.types.chat import ChatCompletion
        except ImportError as e:
            raise ImportError(
                f"OpenAI is required to use the {self.__class__.__name__} class. Please install it with `pip install openai`."
            ) from e
        if not isinstance(response, ChatCompletion):
            raise TypeError("The response is not an OpenAI ChatCompletion object.")

        message = self._get_response_message(response)
        if message.content is None and message.tool_calls is None:
            raise ValueError("The OpenAI ChatCompletion object does not contain a message content or tool calls.")
