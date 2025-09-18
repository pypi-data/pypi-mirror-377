"""
Structured LLM interface using Instructor for reliable structured outputs.

This module provides type-safe structured outputs with automatic validation,
retries, and streaming support. Built on Instructor and Pydantic for maximum
reliability and developer experience.
"""

from typing import Union, List, Dict, Any, Optional, Type, TypeVar, AsyncGenerator, Iterator

try:
    import instructor
    from openai import OpenAI, AsyncOpenAI
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False

from pydantic import BaseModel

from .messages import Messages
from .utils.config_utils import get_llm_config
from .llm import LLMError

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

class StructuredLLMError(LLMError):
    """Exception raised when there's an error in structured LLM operations."""
    pass

def _ensure_instructor_available():
    """Check if Instructor is available and raise helpful error if not."""
    if not INSTRUCTOR_AVAILABLE:
        raise StructuredLLMError(
            "Instructor is not installed. Install it with: pip install instructor"
        )

def _get_instructor_client(
    async_client: bool = False,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
):
    """Get configured Instructor client with same config pattern as regular LLM functions."""
    _ensure_instructor_available()

    # Get configuration using our existing config system (same as regular LLM functions)
    try:
        config = get_llm_config(api_key=api_key, model=model, base_url=base_url)
        api_key_resolved = config["api_key"]
        model_resolved = config["model"]
        base_url_resolved = config["base_url"]
    except ValueError as e:
        raise StructuredLLMError(str(e))

    # Create OpenAI client
    if async_client:
        openai_client = AsyncOpenAI(
            api_key=api_key_resolved,
            base_url=base_url_resolved
        )
    else:
        openai_client = OpenAI(
            api_key=api_key_resolved,
            base_url=base_url_resolved
        )

    # Wrap with Instructor
    return instructor.from_openai(openai_client), config

def _prepare_messages(messages: Union[Messages, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Convert Messages object to list format for Instructor."""
    if isinstance(messages, Messages):
        return messages.get_messages()
    return messages

def call_llm(
    messages: Union[Messages, List[Dict[str, Any]]],
    response_model: Type[T],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    max_retries: int = 3,
    validation_context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> T:
    """
    Call LLM with structured output using Instructor.

    This function has the same signature as the regular call_llm but returns
    structured, validated data instead of raw message objects.

    Args:
        messages: Either a Messages instance or a list of message dicts
        response_model: Pydantic model class defining the expected output structure
        api_key: OpenAI API key (if not provided, loads from .env OPENAI_API_KEY)
        model: Model name to use for completion
        base_url: Base URL for the API (useful for vLLM or OpenRouter endpoints)
        max_retries: Maximum number of retries for validation failures (default: 3)
        validation_context: Optional context dict for validation
        **kwargs: Additional parameters to pass to OpenAI API

    Returns:
        An instance of response_model with validated data

    Raises:
        StructuredLLMError: If API call fails or validation fails after max retries

    Example:
        class PersonInfo(BaseModel):
            name: str
            age: int
            city: str

        messages = Messages(
            system_prompt="Extract person information from text.",
            user_prompt="John is 25 years old and lives in New York."
        )

        person = call_llm(messages, PersonInfo)
        print(f"{person.name} is {person.age} years old")  # Type-safe access
    """
    try:
        client, config = _get_instructor_client(
            async_client=False,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        message_list = _prepare_messages(messages)

        # Prepare completion parameters
        completion_params = {
            "model": config["model"],
            "response_model": response_model,
            "messages": message_list,
            "max_retries": max_retries,
            **kwargs,
        }

        # Add validation context if provided
        if validation_context:
            completion_params["validation_context"] = validation_context

        # Make structured completion request
        result = client.chat.completions.create(**completion_params)
        return result

    except Exception as e:
        raise StructuredLLMError(f"Failed to get structured LLM response: {e}")

async def call_llm_async(
    messages: Union[Messages, List[Dict[str, Any]]],
    response_model: Type[T],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    max_retries: int = 3,
    validation_context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> T:
    """
    Async version of call_llm with structured output.

    Args:
        messages: Either a Messages instance or a list of message dicts
        response_model: Pydantic model class defining the expected output structure
        api_key: OpenAI API key (if not provided, loads from .env OPENAI_API_KEY)
        model: Model name to use for completion
        base_url: Base URL for the API (useful for vLLM or OpenRouter endpoints)
        max_retries: Maximum number of retries for validation failures (default: 3)
        validation_context: Optional context dict for validation
        **kwargs: Additional parameters to pass to OpenAI API

    Returns:
        An instance of response_model with validated data

    Raises:
        StructuredLLMError: If API call fails or validation fails after max retries
    """
    try:
        client, config = _get_instructor_client(
            async_client=True,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        message_list = _prepare_messages(messages)

        # Prepare completion parameters
        completion_params = {
            "model": config["model"],
            "response_model": response_model,
            "messages": message_list,
            "max_retries": max_retries,
            **kwargs,
        }

        # Add validation context if provided
        if validation_context:
            completion_params["validation_context"] = validation_context

        # Make structured completion request
        result = await client.chat.completions.create(**completion_params)
        return result

    except Exception as e:
        raise StructuredLLMError(f"Failed to get structured LLM response: {e}")

def call_llm_stream(
    messages: Union[Messages, List[Dict[str, Any]]],
    response_model: Type[T],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> Iterator[T]:
    """
    Stream structured outputs with partial validation.

    This function has the same signature as the regular call_llm_stream but returns
    structured data with partial updates as the model generates the response.

    Args:
        messages: Either a Messages instance or a list of message dicts
        response_model: Pydantic model class defining the expected output structure
        api_key: OpenAI API key (if not provided, loads from .env OPENAI_API_KEY)
        model: Model name to use for completion
        base_url: Base URL for the API (useful for vLLM or OpenRouter endpoints)
        **kwargs: Additional parameters to pass to OpenAI API

    Returns:
        Iterator yielding partial instances of response_model

    Raises:
        StructuredLLMError: If API call fails

    Example:
        class ArticleSummary(BaseModel):
            title: str
            key_points: List[str]
            conclusion: str

        for partial in call_llm_stream(messages, ArticleSummary):
            print(f"Current title: {partial.title}")
            print(f"Points so far: {len(partial.key_points or [])}")
    """
    try:
        client, config = _get_instructor_client(
            async_client=False,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        message_list = _prepare_messages(messages)

        # Prepare completion parameters
        completion_params = {
            "model": config["model"],
            "response_model": response_model,
            "messages": message_list,
            "stream": True,
            **kwargs,
        }

        # Stream structured completions
        for partial in client.chat.completions.create(**completion_params):
            yield partial

    except Exception as e:
        raise StructuredLLMError(f"Failed to stream structured LLM response: {e}")

async def call_llm_stream_async(
    messages: Union[Messages, List[Dict[str, Any]]],
    response_model: Type[T],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> AsyncGenerator[T, None]:
    """
    Async version of call_llm_stream with structured output.

    Args:
        messages: Either a Messages instance or a list of message dicts
        response_model: Pydantic model class defining the expected output structure
        api_key: OpenAI API key (if not provided, loads from .env OPENAI_API_KEY)
        model: Model name to use for completion
        base_url: Base URL for the API (useful for vLLM or OpenRouter endpoints)
        **kwargs: Additional parameters to pass to OpenAI API

    Returns:
        Async generator yielding partial instances of response_model

    Raises:
        StructuredLLMError: If API call fails
    """
    try:
        client, config = _get_instructor_client(
            async_client=True,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        message_list = _prepare_messages(messages)

        # Prepare completion parameters
        completion_params = {
            "model": config["model"],
            "response_model": response_model,
            "messages": message_list,
            "stream": True,
            **kwargs,
        }

        # Stream structured completions - await the generator
        stream = await client.chat.completions.create(**completion_params)
        async for partial in stream:
            yield partial

    except Exception as e:
        raise StructuredLLMError(f"Failed to stream structured LLM response: {e}")

class StructuredLLMClient:
    """
    High-level client for structured LLM interactions.

    This class provides a convenient interface for both sync and async
    structured LLM operations with consistent configuration.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the structured LLM client.

        Args:
            api_key: OpenAI API key (optional, loads from config if not provided)
            model: Model name (optional, loads from config if not provided)
            base_url: Base URL for API (optional, loads from config if not provided)
        """
        _ensure_instructor_available()

        # Store custom config if provided
        self._custom_config = {}
        if api_key:
            self._custom_config["api_key"] = api_key
        if model:
            self._custom_config["model"] = model
        if base_url:
            self._custom_config["base_url"] = base_url

    def _get_client_and_config(self, async_client: bool = False):
        """Get client and config with custom overrides."""
        if self._custom_config:
            # Merge custom config with defaults
            config = get_llm_config()
            config.update(self._custom_config)

            # Create client with custom config
            if async_client:
                openai_client = AsyncOpenAI(
                    api_key=config["api_key"],
                    base_url=config["base_url"]
                )
            else:
                openai_client = OpenAI(
                    api_key=config["api_key"],
                    base_url=config["base_url"]
                )

            return instructor.from_openai(openai_client), config
        else:
            return _get_instructor_client(async_client=async_client)

    def call(self, messages: Union[Messages, List[Dict[str, Any]]], response_model: Type[T], **kwargs) -> T:
        """Sync structured call."""
        client, config = self._get_client_and_config(async_client=False)
        message_list = _prepare_messages(messages)

        try:
            result = client.chat.completions.create(
                model=config["model"],
                response_model=response_model,
                messages=message_list,
                **kwargs
            )
            return result
        except Exception as e:
            raise StructuredLLMError(f"Failed to get structured response: {e}")

    async def call_async(self, messages: Union[Messages, List[Dict[str, Any]]], response_model: Type[T], **kwargs) -> T:
        """Async structured call."""
        client, config = self._get_client_and_config(async_client=True)
        message_list = _prepare_messages(messages)

        try:
            result = await client.chat.completions.create(
                model=config["model"],
                response_model=response_model,
                messages=message_list,
                **kwargs
            )
            return result
        except Exception as e:
            raise StructuredLLMError(f"Failed to get structured response: {e}")

    def stream(self, messages: Union[Messages, List[Dict[str, Any]]], response_model: Type[T], **kwargs) -> Iterator[T]:
        """Sync structured streaming."""
        client, config = self._get_client_and_config(async_client=False)
        message_list = _prepare_messages(messages)

        try:
            for partial in client.chat.completions.create(
                model=config["model"],
                response_model=response_model,
                messages=message_list,
                stream=True,
                **kwargs
            ):
                yield partial
        except Exception as e:
            raise StructuredLLMError(f"Failed to stream structured response: {e}")

    async def stream_async(self, messages: Union[Messages, List[Dict[str, Any]]], response_model: Type[T], **kwargs) -> AsyncGenerator[T, None]:
        """Async structured streaming."""
        client, config = self._get_client_and_config(async_client=True)
        message_list = _prepare_messages(messages)

        try:
            stream = await client.chat.completions.create(
                model=config["model"],
                response_model=response_model,
                messages=message_list,
                stream=True,
                **kwargs
            )
            async for partial in stream:
                yield partial
        except Exception as e:
            raise StructuredLLMError(f"Failed to stream structured response: {e}")

# Convenience functions that match the naming pattern of existing agentic-blocks functions
def call_llm_sync(
    messages: Union[Messages, List[Dict[str, Any]]],
    response_model: Type[T],
    **kwargs
) -> T:
    """
    Convenience function matching agentic-blocks naming pattern.
    Alias for call_llm.
    """
    return call_llm(messages, response_model, **kwargs)

# Example models for testing and documentation
class ExamplePersonInfo(BaseModel):
    """Example model for person information extraction."""
    name: str
    age: int
    city: str
    occupation: Optional[str] = None

class ExampleMathResult(BaseModel):
    """Example model for mathematical calculations."""
    operation: str
    operand_a: float
    operand_b: float
    result: float
    explanation: str

class ExampleSearchQuery(BaseModel):
    """Example model for search query parsing."""
    query: str
    category: str
    filters: List[str] = []
    estimated_results: int