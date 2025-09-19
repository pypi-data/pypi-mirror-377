from __future__ import annotations

import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import openai
from google import genai

from .base_tool import BaseTool
from .tool_registry import register_tool
from .logging_config import get_logger


@register_tool("AgenticTool")
class AgenticTool(BaseTool):
    """Generic wrapper around LLM prompting supporting JSON-defined configs with prompts and input arguments."""

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        self.logger = get_logger("AgenticTool")  # Initialize logger
        self.name: str = tool_config.get("name", "")  # Add name attribute
        self._prompt_template: str = tool_config.get("prompt", "")
        self._input_arguments: List[str] = tool_config.get("input_arguments", [])

        # Extract required arguments from parameter schema
        parameter_info = tool_config.get("parameter", {})
        self._required_arguments: List[str] = parameter_info.get("required", [])
        self._argument_defaults: Dict[str, str] = {}

        # Set up default values for optional arguments
        properties = parameter_info.get("properties", {})
        for arg in self._input_arguments:
            if arg not in self._required_arguments:
                prop_info = properties.get(arg, {})

                # First check if there's an explicit "default" field
                if "default" in prop_info:
                    self._argument_defaults[arg] = prop_info["default"]

        # Get configuration from nested 'configs' dict or fallback to top-level
        configs = tool_config.get("configs", {})

        # Helper function to get config values with fallback
        def get_config(key: str, default: Any) -> Any:
            return configs.get(key, tool_config.get(key, default))

        # LLM configuration
        self._api_type: str = get_config("api_type", "CHATGPT")
        self._model_id: str = get_config("model_id", "o1-mini")
        self._temperature: float = get_config("temperature", 0.1)
        self._max_new_tokens: int = get_config("max_new_tokens", 2048)
        self._return_json: bool = get_config("return_json", False)
        self._max_retries: int = get_config("max_retries", 5)
        self._retry_delay: int = get_config("retry_delay", 5)
        self.return_metadata: bool = get_config("return_metadata", True)

        # Validation
        if not self._prompt_template:
            raise ValueError("AgenticTool requires a 'prompt' in the configuration.")
        if not self._input_arguments:
            raise ValueError(
                "AgenticTool requires 'input_arguments' in the configuration."
            )

        # Validate temperature range
        if not 0 <= self._temperature <= 2:
            self.logger.warning(
                f"Temperature {self._temperature} is outside recommended range [0, 2]"
            )

        # Validate model compatibility
        self._validate_model_config()

        # Initialize the LLM model
        try:
            self._model, self._tokenizer = self._init_llm(
                api_type=self._api_type, model_id=self._model_id
            )
            self.logger.debug(
                f"Successfully initialized {self._api_type} model: {self._model_id}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM model: {str(e)}")
            raise

    # ------------------------------------------------------------------ LLM utilities -----------
    def _validate_model_config(self):
        """Validate model configuration parameters."""
        supported_api_types = ["CHATGPT", "GEMINI"]
        if self._api_type not in supported_api_types:
            raise ValueError(
                f"Unsupported API type: {self._api_type}. Supported types: {supported_api_types}"
            )

        # Validate model-specific configurations
        # if self._api_type == "CHATGPT":
        #     supported_models = ["gpt-4o", "o1-mini", "o3-mini"]
        #     if self._model_id not in supported_models:
        #         self.logger.warning(f"Model {self._model_id} may not be supported. Supported models: {supported_models}")

        # Validate token limits
        if self._max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be positive")

        if self._max_new_tokens > 8192:  # Conservative limit
            self.logger.warning(
                f"max_new_tokens {self._max_new_tokens} is very high and may cause API issues"
            )

    def _init_llm(self, api_type: str, model_id: str):
        """Initialize the LLM model and tokenizer based on API type."""
        if api_type == "CHATGPT":
            if "gpt-4o" in model_id or model_id is None:
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
                api_version = "2024-12-01-preview"
            elif (
                "o1-mini" in model_id or "o3-mini" in model_id or "o4-mini" in model_id
            ):
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
                api_version = "2025-03-01-preview"
            else:
                self.logger.error(
                    f"Invalid model_id. Please use 'gpt-4o', 'o1-mini', or 'o3-mini'. Got: {model_id}"
                )
                raise ValueError(f"Unsupported model_id: {model_id}")

            if not api_key:
                raise ValueError(
                    "API key not found in environment. Please set the appropriate environment variable."
                )

            azure_endpoint = os.getenv(
                "AZURE_OPENAI_ENDPOINT", "https://azure-ai.hms.edu"
            )

            from openai import AzureOpenAI

            self.logger.debug(
                "Initializing AzureOpenAI client with endpoint:", azure_endpoint
            )
            self.logger.debug("Using API version:", api_version)
            model_client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
            )
            model = {
                "model": model_client,
                "model_name": model_id,
                "api_version": api_version,
            }
            tokenizer = None
        elif api_type == "GEMINI":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")

            model = genai.Client(api_key=api_key)
            tokenizer = None
        else:
            raise ValueError(f"Unsupported API type: {api_type}")

        return model, tokenizer

    def _chatgpt_infer(
        self,
        model: Dict[str, Any],
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_new_tokens: int = 2048,
        return_json: bool = False,
        max_retries: int = 5,
        retry_delay: int = 5,
        custom_format=None,
    ) -> Optional[str]:
        """Inference function for ChatGPT models including o1-mini and o3-mini."""
        model_client = model["model"]
        model_name = model["model_name"]

        retries = 0
        import traceback

        if custom_format is not None:
            response_format = custom_format
            call_function = model_client.chat.completions.parse
        elif return_json:
            response_format = {"type": "json_object"}
            call_function = model_client.chat.completions.create
        else:
            response_format = None
            call_function = model_client.chat.completions.create
        while retries < max_retries:
            try:
                if "gpt-4o" in model_name:
                    responses = call_function(
                        model=model_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_new_tokens,
                        response_format=response_format,
                    )
                elif (
                    "o1-mini" in model_name
                    or "o3-mini" in model_name
                    or "o4-mini" in model_name
                ):
                    responses = call_function(
                        model=model_name,
                        messages=messages,
                        max_completion_tokens=max_new_tokens,
                        response_format=response_format,
                    )
                if custom_format is not None:
                    response = responses.choices[0].message.parsed.model_dump()
                else:
                    response = responses.choices[0].message.content
                # print("\033[92m" + response + "\033[0m")
                # usage = responses.usage
                # print("\033[95m" + str(usage) + "\033[0m")
                return response
            except openai.RateLimitError:
                self.logger.warning(
                    f"Rate limit exceeded. Retrying in {retry_delay} seconds..."
                )
                retries += 1
                time.sleep(retry_delay * retries)
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                traceback.print_exc()
                break
        self.logger.error("Max retries exceeded. Unable to complete the request.")
        return None

    def _gemini_infer(
        self,
        model: Any,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_new_tokens: int = 2048,
        return_json: bool = False,
        max_retries: int = 5,
        retry_delay: int = 5,
        model_name: str = "gemini-2.0-flash",
    ) -> Optional[str]:
        """Inference function for Gemini models."""
        retries = 0
        contents = ""
        for message in messages:
            if message["role"] == "user" or message["role"] == "system":
                contents += f"{message['content']}\n"
            elif message["role"] == "assistant":
                raise ValueError(
                    "Gemini model does not support assistant role in messages for now in the code."
                )
            else:
                raise ValueError(
                    "Invalid role in messages. Only 'user' and 'system' roles are supported."
                )

        if return_json:
            raise ValueError(
                "Gemini model does not support JSON format for now in the code."
            )

        while retries < max_retries:
            try:
                response = model.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=genai.types.GenerateContentConfig(
                        max_output_tokens=max_new_tokens,
                        temperature=temperature,
                    ),
                )
                return response.text
            except openai.RateLimitError:
                self.logger.warning(
                    f"Rate limit exceeded. Retrying in {retry_delay} seconds..."
                )
                retries += 1
                time.sleep(retry_delay * retries)
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                break
        return None

    # ------------------------------------------------------------------ public API --------------
    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool by formatting the prompt with input arguments and querying the LLM."""
        start_time = datetime.now()

        try:
            # Validate that all required input arguments are provided
            missing_required_args = [
                arg for arg in self._required_arguments if arg not in arguments
            ]
            if missing_required_args:
                raise ValueError(
                    f"Missing required input arguments: {missing_required_args}"
                )

            # Add default values for optional arguments that are missing
            for arg in self._input_arguments:
                if arg not in arguments:
                    if arg in self._argument_defaults:
                        arguments[arg] = self._argument_defaults[arg]
                    else:
                        arguments[arg] = ""  # Default to empty string for optional args

            # Validate argument types and content
            self._validate_arguments(arguments)

            # Format the prompt template with the provided arguments
            formatted_prompt = self._format_prompt(arguments)

            # Prepare messages for the LLM
            messages = [{"role": "user", "content": formatted_prompt}]
            custom_format = arguments.get("response_format", None)
            # Call the appropriate LLM function based on API type
            response = self._call_llm(messages, custom_format=custom_format)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            if self.return_metadata:
                return {
                    "success": True,
                    "result": response,
                    "metadata": {
                        "prompt_used": (
                            formatted_prompt
                            if len(formatted_prompt) < 1000
                            else f"{formatted_prompt[:1000]}..."
                        ),
                        "input_arguments": {
                            arg: arguments.get(arg) for arg in self._input_arguments
                        },
                        "model_info": {
                            "api_type": self._api_type,
                            "model_id": self._model_id,
                            "temperature": self._temperature,
                            "max_new_tokens": self._max_new_tokens,
                        },
                        "execution_time_seconds": execution_time,
                        "timestamp": start_time.isoformat(),
                    },
                }
            else:
                return response

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            self.logger.error(f"Error executing {self.name}: {str(e)}")

            if self.return_metadata:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "metadata": {
                        "prompt_used": (
                            formatted_prompt
                            if "formatted_prompt" in locals()
                            else "Failed to format prompt"
                        ),
                        "input_arguments": {
                            arg: arguments.get(arg) for arg in self._input_arguments
                        },
                        "model_info": {
                            "api_type": self._api_type,
                            "model_id": self._model_id,
                        },
                        "execution_time_seconds": execution_time,
                        "timestamp": start_time.isoformat(),
                    },
                }
            else:
                return "error: " + str(e) + " error_type: " + type(e).__name__

    # ------------------------------------------------------------------ helpers -----------------
    def _validate_arguments(self, arguments: Dict[str, Any]):
        """Validate input arguments for common issues."""
        for arg_name, value in arguments.items():
            if arg_name in self._input_arguments:
                # Check for empty strings only for required arguments
                if isinstance(value, str) and not value.strip():
                    if arg_name in self._required_arguments:
                        raise ValueError(
                            f"Required argument '{arg_name}' cannot be empty"
                        )
                    # Optional arguments can be empty, so we skip the check

                # Check for extremely long inputs that might cause issues - silent validation
                if (
                    isinstance(value, str) and len(value) > 100000
                ):  # 100k character limit
                    pass  # Could potentially cause API issues but no need to spam output

    def _format_prompt(self, arguments: Dict[str, Any]) -> str:
        """Format the prompt template with the provided arguments."""
        prompt = self._prompt_template

        # Track which placeholders we actually replace
        replaced_placeholders = set()

        # Replace placeholders in the format {argument_name} with actual values
        for arg_name in self._input_arguments:
            placeholder = f"{{{arg_name}}}"
            value = arguments.get(arg_name, "")

            if placeholder in prompt:
                replaced_placeholders.add(arg_name)
                # Handle special characters and formatting
                if isinstance(value, str):
                    # Simple replacement without complex escaping that was causing issues
                    prompt = prompt.replace(placeholder, str(value))
                else:
                    prompt = prompt.replace(placeholder, str(value))

        # Check for unreplaced expected placeholders (only check our input arguments)
        # _unreplaced_expected = [
        #     arg for arg in self._input_arguments if arg not in replaced_placeholders
        # ]

        # Silent handling - no debug output needed for template patterns in JSON content

        return prompt

    def _call_llm(self, messages: List[Dict[str, str]], custom_format=None) -> str:
        """Make the actual LLM API call using the appropriate function."""
        if self._api_type == "CHATGPT":
            response = self._chatgpt_infer(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_new_tokens=self._max_new_tokens,
                return_json=self._return_json,
                max_retries=self._max_retries,
                retry_delay=self._retry_delay,
                custom_format=custom_format,
            )
            if response is None:
                raise Exception("LLM API call failed after maximum retries")
            return response

        elif self._api_type == "GEMINI":
            response = self._gemini_infer(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_new_tokens=self._max_new_tokens,
                return_json=self._return_json,
                max_retries=self._max_retries,
                retry_delay=self._retry_delay,
            )
            if response is None:
                raise Exception("Gemini API call failed after maximum retries")
            return response

        else:
            raise ValueError(f"Unsupported API type: {self._api_type}")

    def get_prompt_preview(self, arguments: Dict[str, Any]) -> str:
        """Preview how the prompt will look with the given arguments (useful for debugging)."""
        try:
            # Create a copy to avoid modifying the original arguments
            args_copy = arguments.copy()

            # Validate that all required input arguments are provided
            missing_required_args = [
                arg for arg in self._required_arguments if arg not in args_copy
            ]
            if missing_required_args:
                raise ValueError(
                    f"Missing required input arguments: {missing_required_args}"
                )

            # Add default values for optional arguments that are missing
            for arg in self._input_arguments:
                if arg not in args_copy:
                    if arg in self._argument_defaults:
                        args_copy[arg] = self._argument_defaults[arg]
                    else:
                        args_copy[arg] = ""  # Default to empty string for optional args

            return self._format_prompt(args_copy)
        except Exception as e:
            return f"Error formatting prompt: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the configured model."""
        return {
            "api_type": self._api_type,
            "model_id": self._model_id,
            "temperature": self._temperature,
            "max_new_tokens": self._max_new_tokens,
            "return_json": self._return_json,
            "max_retries": self._max_retries,
            "retry_delay": self._retry_delay,
        }

    def get_prompt_template(self) -> str:
        """Get the raw prompt template."""
        return self._prompt_template

    def get_input_arguments(self) -> List[str]:
        """Get the list of required input arguments."""
        return self._input_arguments.copy()

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the tool configuration and return validation results."""
        validation_results = {"valid": True, "warnings": [], "errors": []}

        try:
            self._validate_model_config()
        except ValueError as e:
            validation_results["valid"] = False
            validation_results["errors"].append(str(e))

        # Check prompt template
        if not self._prompt_template:
            validation_results["valid"] = False
            validation_results["errors"].append("Missing prompt template")

        # Check for placeholder consistency
        placeholders_in_prompt = set(re.findall(r"\{([^}]+)\}", self._prompt_template))
        required_args = set(self._input_arguments)

        missing_in_prompt = required_args - placeholders_in_prompt
        extra_in_prompt = placeholders_in_prompt - required_args

        if missing_in_prompt:
            validation_results["warnings"].append(
                f"Arguments not used in prompt: {missing_in_prompt}"
            )

        if extra_in_prompt:
            validation_results["warnings"].append(
                f"Placeholders in prompt without corresponding arguments: {extra_in_prompt}"
            )

        return validation_results

    def estimate_token_usage(self, arguments: Dict[str, Any]) -> Dict[str, int]:
        """Estimate token usage for the given arguments (rough approximation)."""
        prompt = self._format_prompt(arguments)

        # Rough token estimation (4 characters ≈ 1 token for English text)
        estimated_input_tokens = len(prompt) // 4
        estimated_max_output_tokens = self._max_new_tokens
        estimated_total_tokens = estimated_input_tokens + estimated_max_output_tokens

        return {
            "estimated_input_tokens": estimated_input_tokens,
            "max_output_tokens": estimated_max_output_tokens,
            "estimated_total_tokens": estimated_total_tokens,
            "prompt_length_chars": len(prompt),
        }
