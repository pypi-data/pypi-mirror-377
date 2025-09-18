"""AI model interface and provider abstraction with retry support.

All provider calls are wrapped with an exponential backoff retry to cope
with transient failures. The retry behaviour can be configured via
``retries`` parameters on the public methods.

The :class:`AIModelInterface` constructor accepts optional API keys for
multiple providers. Notably, the ``openai_api_key`` and
``anthropic_api_key`` parameters (or the ``OPENAI_API_KEY`` and
``ANTHROPIC_API_KEY`` environment variables) enable OpenAI and
Anthropic models respectively.

This module requires the ``openai`` (version >=1.0), ``google-genai``,
``anthropic``, ``requests``, ``transformers`` and ``diffusers`` packages.
"""

from __future__ import annotations

import asyncio
import base64
import io
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional, Union

from openai import AsyncOpenAI, OpenAI
from google import genai
import anthropic
import requests
from transformers import pipeline as hf_local_pipeline
from diffusers import StableDiffusionPipeline


PromptType = Union[str, List[Dict[str, str]]]


def _retry_sync(func, retries: int = 3, base_delay: float = 0.1) -> Any:
    """Retry ``func`` with exponential backoff."""
    delay = base_delay
    for attempt in range(retries):
        try:
            return func()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


async def _retry_async(func, retries: int = 3, base_delay: float = 0.1) -> Any:
    """Asynchronously retry ``func`` with exponential backoff."""
    delay = base_delay
    for attempt in range(retries):
        try:
            return await func()
        except Exception:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2


def _retry_stream(func, retries: int = 3, base_delay: float = 0.1) -> Iterator[str]:
    """Retry a streaming function yielding from successive attempts."""

    def generator() -> Iterator[str]:
        delay = base_delay
        for attempt in range(retries):
            try:
                yield from func()
                return
            except Exception:
                if attempt == retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

    return generator()


class ModelProvider(ABC):
    """Base class for all model providers.

    See the ``README`` section *Adding a Custom LLM Provider* for
    guidance on implementing subclasses.
    """

    #: Whether the provider natively supports batching multiple prompts in a
    #: single API call. Subclasses can override this to ``True`` when their
    #: backend exposes such functionality.
    supports_batching: bool = False

    def __init__(self, models: Dict[str, str]):
        self.models = models

    def supports(self, model: str) -> bool:
        """Return ``True`` if the provider exposes the requested model."""
        return model in self.models

    @abstractmethod
    def generate_text(self, model: str, prompt: PromptType, max_tokens: int) -> str:
        """Generate text from the given model."""

    async def generate_text_async(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:
        """Asynchronously generate text.

        Providers that expose native async APIs should override this method.
        The default implementation simply delegates to :meth:`generate_text`
        using ``asyncio.to_thread`` to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self.generate_text, model, prompt, max_tokens)

    def stream_generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> Iterator[str]:
        """Yield generated text chunks.

        Providers that support server-side streaming should override this
        method. The base implementation yields the full response in a single
        chunk.
        """
        yield self.generate_text(model, prompt, max_tokens)


class GeminiProvider(ModelProvider):
    """Provider for Google Gemini models."""

    def __init__(self, api_key: str):
        models = {
            "gemini-1.0-pro": "gemini-1.0-pro",
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-2.0-flash": "gemini-2.0-flash",
        }
        super().__init__(models)
        self.client = genai.Client(api_key=api_key)

    def generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover - thin wrapper
        if isinstance(prompt, list):
            prompt = " ".join(
                msg["content"] for msg in prompt if msg.get("role") == "user"
            )
        response = self.client.models.generate_content(model=model, contents=[prompt])
        return response.text

    async def generate_text_async(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover - thin wrapper
        if hasattr(self.client.models, "generate_content_async"):
            if isinstance(prompt, list):
                prompt = " ".join(
                    msg["content"] for msg in prompt if msg.get("role") == "user"
                )
            response = await self.client.models.generate_content_async(
                model=model, contents=[prompt]
            )
            return response.text
        return await super().generate_text_async(model, prompt, max_tokens)

    def stream_generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> Iterator[str]:  # pragma: no cover - thin wrapper
        if isinstance(prompt, list):
            prompt = " ".join(
                msg["content"] for msg in prompt if msg.get("role") == "user"
            )
        stream = self.client.models.generate_content(
            model=model, contents=[prompt], stream=True
        )
        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text


class OpenRouterProvider(ModelProvider):
    """Provider for models available via OpenRouter (e.g., DeepSeek)."""

    def __init__(self, api_key: str):
        models = {
            "deepseek-r1": "deepseek/deepseek-r1:free",
            "deepseek-chat-v3-0324": "deepseek/deepseek-chat-v3-0324:free",
        }
        super().__init__(models)
        self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        self.async_client = AsyncOpenAI(
            api_key=api_key, base_url="https://openrouter.ai/api/v1"
        )

    def generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover
        if isinstance(prompt, str):
            prompt_input: PromptType = [{"role": "user", "content": prompt}]
        else:
            prompt_input = prompt
        response = self.client.responses.create(
            model=self.models[model],
            input=prompt_input,
            max_output_tokens=max_tokens,
        )
        return response.output[0].content[0].text

    async def generate_text_async(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover - thin wrapper
        if isinstance(prompt, str):
            prompt_input: PromptType = [{"role": "user", "content": prompt}]
        else:
            prompt_input = prompt
        response = await self.async_client.responses.create(
            model=self.models[model],
            input=prompt_input,
            max_output_tokens=max_tokens,
        )
        return response.output[0].content[0].text

    def stream_generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> Iterator[str]:  # pragma: no cover - thin wrapper
        if isinstance(prompt, str):
            prompt_input: PromptType = [{"role": "user", "content": prompt}]
        else:
            prompt_input = prompt
        with self.client.responses.stream(
            model=self.models[model],
            input=prompt_input,
            max_output_tokens=max_tokens,
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta


class OpenAIProvider(ModelProvider):
    """Provider for OpenAI's GPT models."""

    def __init__(self, api_key: str):
        models = {
            "gpt-4": "gpt-4",
            "gpt-image-1": "gpt-image-1",
        }
        super().__init__(models)
        self._image_models = {"gpt-image-1"}
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    def generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover
        if isinstance(prompt, str):
            prompt_input: PromptType = [{"role": "user", "content": prompt}]
        else:
            prompt_input = prompt
        response = self.client.responses.create(
            model=self.models[model],
            input=prompt_input,
            max_output_tokens=max_tokens,
        )
        return response.output[0].content[0].text

    async def generate_text_async(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover - thin wrapper
        if isinstance(prompt, str):
            prompt_input: PromptType = [{"role": "user", "content": prompt}]
        else:
            prompt_input = prompt
        response = await self.async_client.responses.create(
            model=self.models[model],
            input=prompt_input,
            max_output_tokens=max_tokens,
        )
        return response.output[0].content[0].text

    def stream_generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> Iterator[str]:  # pragma: no cover - thin wrapper
        if isinstance(prompt, str):
            prompt_input: PromptType = [{"role": "user", "content": prompt}]
        else:
            prompt_input = prompt
        with self.client.responses.stream(
            model=self.models[model],
            input=prompt_input,
            max_output_tokens=max_tokens,
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta

    def generate_image(self, model: str, prompt: str) -> bytes:
        if model not in self._image_models:
            raise ValueError(f"Model '{model}' is not an image model")
        resp = self.client.images.generate(
            model=self.models[model], prompt=prompt, response_format="b64_json"
        )
        data = resp.data[0].b64_json
        return base64.b64decode(data)


class AnthropicProvider(ModelProvider):
    """Provider for Anthropic's Claude models."""

    def __init__(self, api_key: str):
        models = {
            "claude-3-haiku": "claude-3-haiku-20240307",
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-image": "claude-3-opus-20240229",
        }
        super().__init__(models)
        self._image_models = {"claude-image"}
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
        response = self.client.messages.create(
            model=self.models[model],
            max_tokens=max_tokens,
            messages=messages,
        )
        if response.content:
            return response.content[0].text
        return ""

    def generate_image(self, model: str, prompt: str) -> bytes:
        if model not in self._image_models:
            raise ValueError(f"Model '{model}' is not an image model")
        resp = self.client.images.generate(model=self.models[model], prompt=prompt)
        data = resp.data[0].b64_json  # type: ignore[attr-defined]
        return base64.b64decode(data)


class HuggingFaceProvider(ModelProvider):
    """Provider using the HuggingFace Inference API."""

    API_URL = "https://api-inference.huggingface.co/models/{model}"

    def __init__(self, api_key: str):
        models = {
            "distilgpt2": "distilgpt2",
            "stabilityai/stable-diffusion-2": "stabilityai/stable-diffusion-2",
        }
        super().__init__(models)
        self.api_key = api_key

    def generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
        url = self.API_URL.format(model=self.models[model])
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and result and "generated_text" in result[0]:
            return result[0]["generated_text"]
        if isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        return str(result)

    def generate_image(self, model: str, prompt: str) -> bytes:
        """Generate an image using the HuggingFace Inference API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/png",
        }
        data = {"inputs": prompt}
        url = self.API_URL.format(model=self.models[model])
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        return resp.content


class HuggingFaceLocalProvider(ModelProvider):
    """Provider that runs HuggingFace models locally.

    Uses ``transformers`` for text and ``diffusers`` for images. Both text and
    image generation can be configured independently by specifying
    ``text_model`` and/or ``image_model`` when registering the provider. The
    heavy model weights are loaded on first use.
    """

    def __init__(
        self,
        *,
        text_model: Optional[str] = None,
        image_model: Optional[str] = None,
    ):
        models: Dict[str, str] = {}
        if text_model:
            models[text_model] = text_model
        if image_model:
            models[image_model] = image_model
        if not models:
            raise ValueError("At least one of text_model or image_model must be set")
        super().__init__(models)
        self._text_model = text_model
        self._image_model = image_model
        self._text_generator = None
        self._image_pipeline = None

    def _ensure_text_pipeline(self) -> None:
        if self._text_generator is None:
            self._text_generator = hf_local_pipeline(
                "text-generation", model=self._text_model
            )

    def _ensure_image_pipeline(self) -> None:
        if self._image_pipeline is None:
            self._image_pipeline = StableDiffusionPipeline.from_pretrained(
                self._image_model
            )

    def generate_text(
        self, model: str, prompt: PromptType, max_tokens: int
    ) -> str:  # pragma: no cover - optional heavy dependency
        if model != self._text_model or not self._text_model:
            raise ValueError(f"Model '{model}' is not configured for text generation")
        if isinstance(prompt, list):
            prompt = " ".join(
                msg["content"] for msg in prompt if msg.get("role") == "user"
            )
        self._ensure_text_pipeline()
        result = self._text_generator(prompt, max_new_tokens=max_tokens)
        return result[0]["generated_text"]

    def generate_image(self, model: str, prompt: str) -> bytes:  # pragma: no cover
        if model != self._image_model or not self._image_model:
            raise ValueError(f"Model '{model}' is not configured for image generation")
        self._ensure_image_pipeline()
        image = self._image_pipeline(prompt).images[0]
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()


class AIModelInterface:
    """Register and dispatch to different AI model providers."""

    _PROVIDER_CLASSES = {
        "gemini": GeminiProvider,
        "openrouter": OpenRouterProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "huggingface": HuggingFaceProvider,
        "huggingface_local": HuggingFaceLocalProvider,
    }

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        huggingface_api_key: Optional[str] = None,
        enabled_providers: Optional[List[str]] = None,
    ):
        """Initialise the interface and register available providers.

        The interface accepts optional API keys for different large language
        model providers. The ``openai_api_key`` and ``anthropic_api_key``
        parameters, or their respective ``OPENAI_API_KEY`` and
        ``ANTHROPIC_API_KEY`` environment variables, enable OpenAI and
        Anthropic support.

        Parameters
        ----------
        gemini_api_key : str, optional
            API key for Google Gemini.
        openrouter_api_key : str, optional
            API key for OpenRouter.
        openai_api_key : str, optional
            API key for OpenAI. Defaults to ``OPENAI_API_KEY`` environment
            variable if not provided.
        anthropic_api_key : str, optional
            API key for Anthropic. Defaults to ``ANTHROPIC_API_KEY`` environment
            variable if not provided.
        huggingface_api_key : str, optional
            API key for HuggingFace Inference API. Defaults to
            ``HUGGINGFACE_API_KEY`` or ``HUGGINGFACEHUB_API_TOKEN`` environment
            variables.
        enabled_providers : list[str], optional
            Restrict registration to this subset of providers. By default, all
            providers with available API keys are enabled.
        """
        env_providers = os.environ.get("AI_MODEL_PROVIDERS")
        if enabled_providers is None and env_providers:
            enabled_providers = [
                p.strip() for p in env_providers.split(",") if p.strip()
            ]

        self._providers: Dict[str, ModelProvider] = {}

        provider_kwargs = {
            "gemini": gemini_api_key or os.environ.get("GEMINI_API_KEY"),
            "openrouter": openrouter_api_key or os.environ.get("OPENROUTER_API_KEY"),
            "openai": openai_api_key or os.environ.get("OPENAI_API_KEY"),
            "anthropic": anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY"),
            "huggingface": huggingface_api_key
            or os.environ.get("HUGGINGFACE_API_KEY")
            or os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
        }

        for name in self._PROVIDER_CLASSES:
            if enabled_providers is not None and name not in enabled_providers:
                continue
            api_key = provider_kwargs.get(name)
            if not api_key:
                continue
            try:
                self.register_provider(name, api_key=api_key)
            except Exception:
                continue

    def register_provider(
        self,
        provider: Union[ModelProvider, str],
        *,
        enabled: bool = True,
        **config: Any,
    ) -> None:
        """Register a provider and its models.

        Parameters
        ----------
        provider : ModelProvider | str
            Either an instantiated provider or the name of a provider defined in
            :attr:`_PROVIDER_CLASSES`.
        enabled : bool, optional
            When ``False`` the provider is skipped.
        **config : dict, optional
            Configuration forwarded to the provider constructor when ``provider``
            is given as a string.
        """
        if not enabled:
            return
        if isinstance(provider, str):
            cls = self._PROVIDER_CLASSES.get(provider)
            if cls is None:
                raise ValueError(f"Unknown provider '{provider}'")
            provider_obj = cls(**config)
        else:
            provider_obj = provider
        for model in provider_obj.models:
            self._providers[model] = provider_obj

    def supports(self, model: str) -> bool:
        """Return whether ``model`` is registered with any provider."""
        return model in self._providers

    def supports_batching(self, model: str) -> bool:
        """Return whether the provider for ``model`` supports batching."""
        provider = self._providers.get(model)
        if provider is None:
            available = list(self._providers.keys())
            raise ValueError(
                f"Model '{model}' not supported. Available models: {available}"
            )
        return getattr(provider, "supports_batching", False)

    def generate_text(
        self,
        model: str,
        prompt: PromptType,
        max_tokens: int = 1000,
        retries: int = 3,
    ) -> str:
        """Generate text using a registered model with retry.

        Parameters
        ----------
        model, prompt, max_tokens : see :meth:`ModelProvider.generate_text`
        retries : int
            Number of attempts before raising the final error.
        """
        provider = self._providers.get(model)
        if provider is None:
            available = list(self._providers.keys())
            raise ValueError(
                f"Model '{model}' not supported. Available models: {available}"
            )
        try:
            return _retry_sync(
                lambda: provider.generate_text(model, prompt, max_tokens=max_tokens),
                retries=retries,
            )
        except Exception as e:  # pragma: no cover - simple re-raise
            raise RuntimeError(f"Error generating response with {model}: {e}") from e

    async def generate_text_async(
        self,
        model: str,
        prompt: PromptType,
        max_tokens: int = 1000,
        retries: int = 3,
    ) -> str:
        """Asynchronously generate text using a registered model with retry.

        Parameters
        ----------
        model, prompt, max_tokens : see :meth:`ModelProvider.generate_text`
        retries : int
            Number of attempts before raising the final error.
        """
        provider = self._providers.get(model)
        if provider is None:
            available = list(self._providers.keys())
            raise ValueError(
                f"Model '{model}' not supported. Available models: {available}"
            )
        try:
            return await _retry_async(
                lambda: provider.generate_text_async(
                    model, prompt, max_tokens=max_tokens
                ),
                retries=retries,
            )
        except Exception as e:  # pragma: no cover - simple re-raise
            raise RuntimeError(f"Error generating response with {model}: {e}") from e

    def stream_generate_text(
        self,
        model: str,
        prompt: PromptType,
        max_tokens: int = 1000,
        retries: int = 3,
    ) -> Iterator[str]:
        """Stream generated text chunks from a registered model with retry.

        Parameters
        ----------
        model, prompt, max_tokens : see
            :meth:`ModelProvider.stream_generate_text`
        retries : int
            Number of attempts before raising the final error.
        """
        provider = self._providers.get(model)
        if provider is None:
            available = list(self._providers.keys())
            raise ValueError(
                f"Model '{model}' not supported. Available models: {available}"
            )
        try:
            return _retry_stream(
                lambda: provider.stream_generate_text(
                    model, prompt, max_tokens=max_tokens
                ),
                retries=retries,
            )
        except Exception as e:  # pragma: no cover - simple re-raise
            raise RuntimeError(f"Error generating response with {model}: {e}") from e

    def generate_image(
        self,
        model: str,
        prompt: str,
        retries: int = 3,
        **kwargs: Any,
    ) -> bytes:
        """Generate an image using a registered model with retry."""
        provider = self._providers.get(model)
        if provider is None or not hasattr(provider, "generate_image"):
            available = [
                m for m, p in self._providers.items() if hasattr(p, "generate_image")
            ]
            raise ValueError(
                f"Model '{model}' not supported for image generation. "
                f"Available image models: {available}"
            )
        try:
            return _retry_sync(
                lambda: getattr(provider, "generate_image")(model, prompt, **kwargs),
                retries=retries,
            )
        except Exception as e:  # pragma: no cover - simple re-raise
            raise RuntimeError(f"Error generating image with {model}: {e}") from e

    def list_available_models(self) -> List[str]:
        """Return the list of registered model names."""
        return list(self._providers.keys())


__all__ = [
    "AIModelInterface",
    "ModelProvider",
    "PromptType",
]
