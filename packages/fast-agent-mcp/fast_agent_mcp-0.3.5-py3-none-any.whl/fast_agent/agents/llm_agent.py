"""
LLM Agent class that adds interaction behaviors to LlmDecorator.

This class extends LlmDecorator with LLM-specific interaction behaviors including:
- UI display methods for messages, tools, and prompts
- Stop reason handling
- Tool call tracking
- Chat display integration
"""

from typing import List, Optional, Tuple

try:
    from a2a.types import AgentCapabilities  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    from dataclasses import dataclass

    @dataclass
    class AgentCapabilities:  # minimal fallback
        streaming: bool = False
        push_notifications: bool = False
        state_transition_history: bool = False


from mcp import Tool
from rich.text import Text

from fast_agent.agents.agent_types import AgentConfig
from fast_agent.agents.llm_decorator import LlmDecorator, ModelT
from fast_agent.context import Context
from fast_agent.types import PromptMessageExtended, RequestParams
from fast_agent.types.llm_stop_reason import LlmStopReason
from fast_agent.ui.console_display import ConsoleDisplay

# TODO -- decide what to do with type safety for model/chat_turn()

DEFAULT_CAPABILITIES = AgentCapabilities(
    streaming=False, push_notifications=False, state_transition_history=False
)


class LlmAgent(LlmDecorator):
    """
    An LLM agent that adds interaction behaviors to the base LlmDecorator.

    This class provides LLM-specific functionality including UI display methods,
    tool call tracking, and chat interaction patterns while delegating core
    LLM operations to the attached AugmentedLLMProtocol.
    """

    def __init__(
        self,
        config: AgentConfig,
        context: Context | None = None,
    ) -> None:
        super().__init__(config=config, context=context)

        # Initialize display component
        self.display = ConsoleDisplay(config=self._context.config if self._context else None)

    async def show_assistant_message(
        self,
        message: PromptMessageExtended,
        bottom_items: List[str] | None = None,
        highlight_items: str | List[str] | None = None,
        max_item_length: int | None = None,
        name: str | None = None,
        model: str | None = None,
        additional_message: Optional[Text] = None,
    ) -> None:
        """Display an assistant message with appropriate styling based on stop reason.

        Args:
            message: The message to display
            bottom_items: Optional items for bottom bar (e.g., servers, destinations)
            highlight_items: Items to highlight in bottom bar
            max_item_length: Max length for bottom items
            name: Optional agent name to display
            model: Optional model name to display
            additional_message: Optional additional message to display
        """

        # Determine display content based on stop reason if not provided
        if additional_message is None:
            # Generate additional message based on stop reason
            match message.stop_reason:
                case LlmStopReason.END_TURN:
                    # No additional message needed for normal end turn
                    additional_message_text = None

                case LlmStopReason.MAX_TOKENS:
                    additional_message_text = Text(
                        "\n\nMaximum output tokens reached - generation stopped.",
                        style="dim red italic",
                    )

                case LlmStopReason.SAFETY:
                    additional_message_text = Text(
                        "\n\nContent filter activated - generation stopped.", style="dim red italic"
                    )

                case LlmStopReason.PAUSE:
                    additional_message_text = Text(
                        "\n\nLLM has requested a pause.", style="dim green italic"
                    )

                case LlmStopReason.STOP_SEQUENCE:
                    additional_message_text = Text(
                        "\n\nStop Sequence activated - generation stopped.", style="dim red italic"
                    )

                case LlmStopReason.TOOL_USE:
                    if None is message.last_text():
                        additional_message_text = Text(
                            "The assistant requested tool calls", style="dim green italic"
                        )
                    else:
                        additional_message_text = None

                case _:
                    if message.stop_reason:
                        additional_message_text = Text(
                            f"\n\nGeneration stopped for an unhandled reason ({message.stop_reason})",
                            style="dim red italic",
                        )
                    else:
                        additional_message_text = None
        else:
            # Use provided additional message
            additional_message_text = (
                additional_message if isinstance(additional_message, Text) else None
            )

        message_text = message.last_text() or ""

        # Use provided name/model or fall back to defaults
        display_name = name if name is not None else self.name
        display_model = model if model is not None else (self.llm.model_name if self._llm else None)

        await self.display.show_assistant_message(
            message_text,
            bottom_items=bottom_items,
            highlight_items=highlight_items,
            max_item_length=max_item_length,
            name=display_name,
            model=display_model,
            additional_message=additional_message_text,
        )

    def show_user_message(self, message: PromptMessageExtended) -> None:
        """Display a user message in a formatted panel."""
        model = self.llm.model_name
        chat_turn = self._llm.chat_turn()
        self.display.show_user_message(message.last_text() or "", model, chat_turn, name=self.name)

    async def generate_impl(
        self,
        messages: List[PromptMessageExtended],
        request_params: RequestParams | None = None,
        tools: List[Tool] | None = None,
    ) -> PromptMessageExtended:
        """
        Enhanced generate implementation that resets tool call tracking.
        Messages are already normalized to List[PromptMessageExtended].
        """
        if "user" == messages[-1].role:
            self.show_user_message(message=messages[-1])

        # TODO -- we should merge the request parameters here with the LLM defaults?
        # TODO - manage error catch, recovery, pause
        result = await super().generate_impl(messages, request_params, tools)

        await self.show_assistant_message(result)
        return result

    async def structured_impl(
        self,
        messages: List[PromptMessageExtended],
        model: type[ModelT],
        request_params: RequestParams | None = None,
    ) -> Tuple[ModelT | None, PromptMessageExtended]:
        if "user" == messages[-1].role:
            self.show_user_message(message=messages[-1])

        result, message = await super().structured_impl(messages, model, request_params)
        await self.show_assistant_message(message=message)
        return result, message

    # async def show_prompt_loaded(
    #     self,
    #     prompt_name: str,
    #     description: Optional[str] = None,
    #     message_count: int = 0,
    #     arguments: Optional[dict[str, str]] = None,
    # ) -> None:
    #     """
    #     Display information about a loaded prompt template.

    #     Args:
    #         prompt_name: The name of the prompt
    #         description: Optional description of the prompt
    #         message_count: Number of messages in the prompt
    #         arguments: Optional dictionary of arguments passed to the prompt
    #     """
    #     # Get aggregator from attached LLM if available
    #     aggregator = None
    #     if self._llm and hasattr(self._llm, "aggregator"):
    #         aggregator = self._llm.aggregator

    #     await self.display.show_prompt_loaded(
    #         prompt_name=prompt_name,
    #         description=description,
    #         message_count=message_count,
    #         agent_name=self.name,
    #         aggregator=aggregator,
    #         arguments=arguments,
    #     )
