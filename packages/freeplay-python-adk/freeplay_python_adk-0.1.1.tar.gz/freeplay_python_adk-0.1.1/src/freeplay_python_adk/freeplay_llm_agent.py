import json
import re
from typing import Any, Literal, Optional

from freeplay import Freeplay
from freeplay.model import InputVariables
from freeplay.resources.prompts import TemplatePrompt
from freeplay.support import TemplateChatMessage, TemplateMessage
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.base_agent import AfterAgentCallback, BeforeAgentCallback
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import (
    AfterModelCallback,
    AfterToolCallback,
    BeforeModelCallback,
    BeforeToolCallback,
    ToolUnion,
)
from google.adk.code_executors.base_code_executor import BaseCodeExecutor
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.planners.base_planner import BasePlanner
from google.genai import types
from opentelemetry import trace
from pydantic import BaseModel

from freeplay_python_adk.client import get_global_config


class InvalidConfigurationError(ValueError):
    def __init__(self):
        super().__init__(
            "No Freeplay configuration found. Either call FreeplayADK.init() first or provide project_id, environment, and freeplay parameters explicitly."
        )


def FreeplayLLMAgent(  # noqa: PLR0913 PLR0915
    name: str,
    *,
    # Freeplay-specific optional configuration (can be None due to global config)
    input_variables: Optional[InputVariables] = None,
    project_id: Optional[str] = None,
    environment: Optional[str] = None,
    freeplay: Optional[Freeplay] = None,
    # LlmAgent parameters (excluding model and instruction which is determined from prompt template)
    tools: Optional[list[ToolUnion]] = None,
    generate_content_config: Optional[types.GenerateContentConfig] = None,
    # Transfer configurations
    disallow_transfer_to_parent: bool = False,
    disallow_transfer_to_peers: bool = False,
    # Content inclusion
    include_contents: Literal["default", "none"] = "default",
    # Input/output configurations
    input_schema: Optional[type[BaseModel]] = None,
    output_schema: Optional[type[BaseModel]] = None,
    output_key: Optional[str] = None,
    # Advanced features
    planner: Optional[BasePlanner] = None,
    code_executor: Optional[BaseCodeExecutor] = None,
    # Callbacks
    before_model_callback: Optional[BeforeModelCallback] = None,
    after_model_callback: Optional[AfterModelCallback] = None,
    before_tool_callback: Optional[BeforeToolCallback] = None,
    after_tool_callback: Optional[AfterToolCallback] = None,
    # Base Agent parameters
    description: str = "",
    sub_agents: Optional[list[BaseAgent]] = None,
    before_agent_callback: Optional[BeforeAgentCallback] = None,
    after_agent_callback: Optional[AfterAgentCallback] = None,
) -> LlmAgent:
    # Handle default for mutable argument
    if tools is None:
        tools = []
    if sub_agents is None:
        sub_agents = []

    input_variables = input_variables or {}

    # Use explicit parameters if provided, otherwise fall back to global config
    if project_id is None or environment is None or freeplay is None:
        global_config = get_global_config()
        if global_config is None:
            raise InvalidConfigurationError()

        project_id = project_id or global_config.project_id
        environment = environment or global_config.environment
        freeplay = freeplay or global_config.freeplay

    prompt_template = freeplay.prompts.get(
        project_id=project_id,
        template_name=name,
        environment=environment,
    )
    if prompt_template.prompt_info.provider == "vertex":
        # Avoid going through LiteLlm for Gemini models.
        model = prompt_template.prompt_info.model
    else:
        model = LiteLlm(
            model=lite_llm_model_string(prompt_template),
        )

    def _update_prompt(callback_context: CallbackContext, llm_request: LlmRequest):
        # Google ADK does a bunch of system message manipulation to add
        # information about what agents are available to call, so we preserve
        # that and pass it through agent_context.
        callback_context.state["freeplay.agent_context"] = (
            llm_request.config.system_instruction
        )
        _input_variables = relevant_variables(
            prompt_template,
            sanitize(
                {
                    **input_variables,
                    **callback_context.state.to_dict(),
                    "agent_context": str(llm_request.config.system_instruction),
                }
            ),
        )
        bound_prompt = prompt_template.bind(
            _input_variables,
            # This is a weird one because history is added through different
            # mechanisms, we just use the system prompt here.
            history=[],
        )
        formatted_prompt = bound_prompt.format(flavor_name="openai_chat")
        llm_request.config.system_instruction = formatted_prompt.system_content

        # Model parameters
        prompt_params = bound_prompt.prompt_info.model_parameters
        if "temperature" in prompt_params:
            llm_request.config.temperature = prompt_params["temperature"]
        if "top_p" in prompt_params:
            llm_request.config.top_p = prompt_params["top_p"]

        if "max_output_tokens" in prompt_params:
            llm_request.config.max_output_tokens = prompt_params["max_output_tokens"]
        elif "max_completion_tokens" in prompt_params:
            llm_request.config.max_output_tokens = prompt_params[
                "max_completion_tokens"
            ]
        elif "max_tokens" in prompt_params:
            llm_request.config.max_output_tokens = prompt_params["max_tokens"]

    def _add_record_info(
        callback_context: CallbackContext,
        llm_response: LlmResponse,  # noqa: ARG001
    ):
        span = trace.get_current_span()

        span.set_attribute(
            "freeplay.prompt-template-version-id",
            prompt_template.prompt_info.prompt_template_version_id,
        )
        span.set_attribute(
            "freeplay.environment",
            environment,
        )

        _input_variables = relevant_variables(
            prompt_template,
            sanitize(
                {
                    **input_variables,
                    **callback_context.state.to_dict(),
                    "agent_context": callback_context.state["freeplay.agent_context"],
                }
            ),
        )
        span.set_attribute(
            "freeplay.input-variables",
            json.dumps(_input_variables),
        )

    # Handle before_model_callback
    before_model_callbacks = []
    if before_model_callback:
        if isinstance(before_model_callback, list):
            before_model_callbacks.extend(before_model_callback)
        else:
            before_model_callbacks.append(before_model_callback)
    before_model_callbacks.append(_update_prompt)

    # Handle after_model_callback
    after_model_callbacks = []
    if after_model_callback:
        if isinstance(after_model_callback, list):
            after_model_callbacks.extend(after_model_callback)
        else:
            after_model_callbacks.append(after_model_callback)
    after_model_callbacks.append(_add_record_info)

    return LlmAgent(
        name=name,
        model=model,
        tools=tools,
        generate_content_config=generate_content_config,
        disallow_transfer_to_parent=disallow_transfer_to_parent,
        disallow_transfer_to_peers=disallow_transfer_to_peers,
        include_contents=include_contents,
        input_schema=input_schema,
        output_schema=output_schema,
        output_key=output_key,
        planner=planner,
        code_executor=code_executor,
        before_model_callback=before_model_callbacks,
        after_model_callback=after_model_callbacks,
        before_tool_callback=before_tool_callback,
        after_tool_callback=after_tool_callback,
        description=description,
        sub_agents=sub_agents,
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )


def lite_llm_model_string(prompt_template: TemplatePrompt) -> str:
    provider = prompt_template.prompt_info.provider
    model = prompt_template.prompt_info.model
    if prompt_template.prompt_info.provider == "vertex":
        provider = "gemini"

    return f"{provider}/{model}"


mustache_variable_pattern = re.compile(r"{{(\w+)}}")


def extract_variable_name(message: TemplateMessage) -> list[str]:
    if not isinstance(message, TemplateChatMessage):
        return []
    return mustache_variable_pattern.findall(message.content)


def relevant_variables(
    prompt_template: TemplatePrompt, variables: dict[Any, Any]
) -> dict[Any, Any]:
    all_variables = {
        variable
        for message in prompt_template.messages
        for variable in extract_variable_name(message)
    }
    return {key: value for key, value in variables.items() if key in all_variables}


def sanitize(data: Any) -> Any:
    if isinstance(data, (str, int, float, bool)):
        return data
    if isinstance(data, dict):
        return {
            key: sanitize(value) for key, value in data.items() if isinstance(key, str)
        }
    if isinstance(data, list):
        return [sanitize(item) for item in data]
    return None
