"""
Inference Manager Module

Handles multi-provider LLM inference with automatic provider selection,
metrics collection, and integration with Promptlyzer prompt management.

Features:
- Multi-provider support (OpenAI, Anthropic, Together AI)
- Automatic provider selection based on model
- Cost tracking and latency monitoring
- Metrics aggregation and reporting
- Promptlyzer prompt integration

Author: Promptlyzer Team
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Generator
from collections import defaultdict
import json
import os
import logging
import sys

from .base import InferenceProvider, InferenceResponse, InferenceMetrics, ModelProvider, StreamChunk
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .together_provider import TogetherProvider

# Configure logging
logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in sync context, handling Jupyter notebooks."""
    try:
        # Check if we're in IPython/Jupyter
        import IPython
        ipython = IPython.get_ipython()
        if ipython and hasattr(ipython, 'kernel'):
            # We're in Jupyter, use nest_asyncio
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(coro)
    except ImportError:
        pass
    
    # Check if there's already an event loop running
    try:
        loop = asyncio.get_running_loop()
        # If we get here, we're in an async context
        # Run in a new thread to avoid conflicts
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop running, we can create one
        return asyncio.run(coro)


class InferenceManager:
    """
    Manages multi-provider LLM inference and metrics collection.
    
    This manager coordinates between different LLM providers, automatically
    selects appropriate providers based on model names, tracks usage metrics,
    and integrates with Promptlyzer's prompt management system.
    
    Attributes:
        providers: Dictionary of configured providers
        metrics_buffer: Buffer for metrics awaiting submission
        metrics_summary: Aggregated metrics by provider
        promptlyzer_client: Reference to parent Promptlyzer client
    
    Example:
        >>> manager = InferenceManager(promptlyzer_client)
        >>> manager.add_provider("openai", "sk-...")
        >>> response = await manager.infer_async("Hello", model="gpt-3.5-turbo")
    """
    
    def __init__(self, promptlyzer_client=None):
        """
        Initialize the InferenceManager.
        
        Args:
            promptlyzer_client: Optional reference to parent PromptlyzerClient
                               for prompt fetching and API submission.
        """
        self.providers: Dict[str, InferenceProvider] = {}
        self.metrics_buffer: List[InferenceMetrics] = []
        self.metrics_summary = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "average_latency_ms": 0.0,
            "uptime_percentage": 100.0,
            "models": defaultdict(lambda: {
                "requests": 0,
                "cost": 0.0,
                "tokens": 0,
                "average_latency_ms": 0.0
            })
        })
        self.promptlyzer_client = promptlyzer_client
        self.metrics_file = "inference_metrics.json"
        
        # Backend inference settings
        self.use_backend_credits = True  # Default: use Promptlyzer credits
        self.external_api_keys = {}  # User's own API keys
        
        # Adaptive metrics submission settings
        self.metrics_batch_size = 50   # Regular batch size
        self.early_batch_size = 5      # First batch for quick feedback
        self.last_metrics_submission = datetime.now(timezone.utc)
        self.total_requests_count = 0  # Total requests since start
        self.has_sent_early_batch = None  # Will be determined on first request
        self.first_check_done = False  # Track if we've done the first-time check
        
        # Load existing metrics if available
        self._load_metrics()
    
    def _validate_optimization_data(self, optimization_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate and normalize optimization data.
        
        Args:
            optimization_data: Raw optimization data from user
            
        Returns:
            Validated optimization data or None
        """
        if not optimization_data:
            return None
        
        # Ensure it's a dict
        if not isinstance(optimization_data, dict):
            logger.warning("optimization_data must be a dictionary, ignoring")
            return None
        
        # Validate known fields
        validated = {}
        
        # System message (string)
        if "system_message" in optimization_data:
            validated["system_message"] = str(optimization_data["system_message"])
        
        # User question (string)
        if "user_question" in optimization_data:
            validated["user_question"] = str(optimization_data["user_question"])
        
        # Context (dict or serializable object)
        if "context" in optimization_data:
            context = optimization_data["context"]
            if isinstance(context, dict):
                validated["context"] = context
            else:
                # Try to convert to dict
                try:
                    validated["context"] = dict(context)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Context must be a dictionary, skipping: {e}")
        
        # Messages (list of dicts)
        if "messages" in optimization_data:
            messages = optimization_data["messages"]
            if isinstance(messages, list):
                validated_messages = []
                for msg in messages:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        validated_messages.append({
                            "role": str(msg["role"]),
                            "content": str(msg["content"])
                        })
                if validated_messages:
                    validated["messages"] = validated_messages
            else:
                logger.warning("Messages must be a list of dicts, skipping")
        
        # Previous messages (deprecated but still supported)
        if "previous_messages" in optimization_data and "messages" not in validated:
            validated["messages"] = optimization_data["previous_messages"]
        
        # Expected output/answer (for quality measurement)
        if "expected_output" in optimization_data:
            validated["expected_output"] = str(optimization_data["expected_output"])
        elif "expected_answer" in optimization_data:
            validated["expected_answer"] = str(optimization_data["expected_answer"])
        
        # Additional metadata
        for key in ["question_type", "context_type", "category"]:
            if key in optimization_data:
                validated[key] = str(optimization_data[key])
        
        return validated if validated else None
    
    def configure_mode(self, use_credits: bool = True) -> None:
        """
        Configure inference mode.
        
        Args:
            use_credits: If True, use Promptlyzer credits (backend).
                        If False, use user's own API keys.
        
        Example:
            >>> manager.configure_mode(use_credits=True)  # Use Promptlyzer credits
            >>> manager.configure_mode(use_credits=False) # Use own API keys
        """
        self.use_backend_credits = use_credits
        logger.info(f"Inference mode set to: {'Backend Credits' if use_credits else 'External API Keys'}")
    
    def add_external_api_key(self, provider: str, api_key: str, base_url: Optional[str] = None) -> None:
        """
        Add user's own API key for external provider usage.
        
        Args:
            provider: Provider name ('openai', 'anthropic', 'together')
            api_key: User's API key for the provider
            base_url: Optional custom base URL
        
        Example:
            >>> manager.add_external_api_key("openai", "sk-...")
        """
        self.external_api_keys[provider.lower()] = {
            "api_key": api_key,
            "base_url": base_url
        }
        logger.info(f"External API key added for {provider}")
    
    def add_provider(self, provider_type: Union[str, ModelProvider], api_key: str, base_url: Optional[str] = None) -> None:
        """
        Add or update an inference provider configuration.
        
        Args:
            provider_type: Provider name as string or ModelProvider enum.
                          Supported: 'openai', 'anthropic', 'together'
            api_key: API key for the provider
            base_url: Optional custom base URL for the provider API
            
        Raises:
            ValueError: If provider type is not supported
            
        Example:
            >>> manager.add_provider("openai", "sk-...")
            >>> manager.add_provider(ModelProvider.ANTHROPIC, "sk-ant-...")
        """
        if isinstance(provider_type, str):
            provider_type = ModelProvider(provider_type.lower())
        
        if provider_type == ModelProvider.OPENAI:
            self.providers["openai"] = OpenAIProvider(api_key, base_url)
        elif provider_type == ModelProvider.ANTHROPIC:
            self.providers["anthropic"] = AnthropicProvider(api_key, base_url)
        elif provider_type == ModelProvider.TOGETHER:
            self.providers["together"] = TogetherProvider(api_key, base_url)
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models grouped by provider."""
        models = {}
        for provider_name, provider in self.providers.items():
            models[provider_name] = provider.get_supported_models()
        return models
    
    def get_provider_for_model(self, model: str) -> Optional[InferenceProvider]:
        """Find the provider that supports a given model."""
        for provider_name, provider in self.providers.items():
            if model in provider.get_supported_models():
                return provider
        return None
    
    async def infer_async(
        self,
        prompt: Union[str, Dict[str, Any]],
        model: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        project_id: Optional[str] = None,
        prompt_name: Optional[str] = None,
        session_id: Optional[str] = None,
        optimization_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[InferenceResponse, AsyncGenerator[StreamChunk, None]]:
        """Perform async inference with automatic provider selection.
        
        Args:
            prompt: Either a string prompt or a dict with project_id and prompt_name
            model: Model to use for inference
            provider: Optional provider override
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            project_id: Project ID for Promptlyzer prompt (used with prompt_name)
            prompt_name: Promptlyzer prompt name (used with project_id)
            session_id: Optional session ID for conversation tracking
            optimization_data: Optional data for prompt optimization including:
                - system_message: The system prompt to optimize
                - user_question: The actual user question
                - context: Any additional context (order info, etc)
                - messages: Previous conversation messages
            **kwargs: Additional provider-specific arguments
        """
        # Check if using backend credits
        if self.use_backend_credits or (not self.providers and not self.external_api_keys):
            # Use backend inference
            return await self._infer_via_backend(
                prompt=prompt,
                model=model,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                system_prompt=system_prompt,
                project_id=project_id,
                session_id=session_id,
                optimization_data=optimization_data,
                collect_optimization_data=kwargs.get("collect_optimization_data", True),
                **kwargs
            )
        
        # Original logic for direct provider inference
        # Validate optimization data
        validated_optimization_data = self._validate_optimization_data(optimization_data)
        
        # Handle prompt resolution
        actual_prompt = prompt
        prompt_metadata = {}
        
        if isinstance(prompt, dict):
            # Dict format: {"project_id": "...", "prompt_name": "..."}
            project_id = prompt.get("project_id")
            prompt_name = prompt.get("prompt_name")
            
            if project_id and prompt_name and self.promptlyzer_client:
                # Fetch from Promptlyzer
                prompt_data = self.promptlyzer_client.get_prompt(project_id, prompt_name)
                actual_prompt = prompt_data.get("content", "")
                prompt_metadata = {
                    "source": "promptlyzer",
                    "project_id": project_id,
                    "prompt_name": prompt_name,
                    "version": prompt_data.get("version")
                }
            else:
                # Use the string value if available
                actual_prompt = prompt.get("content", str(prompt))
        elif project_id and prompt_name and self.promptlyzer_client:
            # Use individual parameters
            prompt_data = self.promptlyzer_client.get_prompt(project_id, prompt_name)
            actual_prompt = prompt_data.get("content", "")
            prompt_metadata = {
                "source": "promptlyzer",
                "project_id": project_id,
                "prompt_name": prompt_name,
                "version": prompt_data.get("version")
            }
        else:
            # Direct string prompt
            actual_prompt = str(prompt)
            prompt_metadata = {"source": "direct"}
        
        # Find provider
        if provider:
            inference_provider = self.providers.get(provider)
            if not inference_provider:
                raise ValueError(f"Provider '{provider}' not configured")
        else:
            # Auto-detect provider from model
            inference_provider = self.get_provider_for_model(model)
            if not inference_provider:
                raise ValueError(f"No provider found for model '{model}'")
        
        # Perform inference
        if stream:
            # For streaming, return a generator that yields chunks
            async def stream_with_metrics():
                result = await inference_provider.infer_async(
                    prompt=actual_prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    system_prompt=system_prompt,
                    **kwargs
                )
                async for chunk in result:
                    # If it's the final chunk with metrics, collect them
                    if chunk.is_final and chunk.metrics:
                        chunk.metrics.prompt_metadata = prompt_metadata
                        chunk.metrics.session_id = session_id
                        chunk.metrics.optimization_data = validated_optimization_data
                        self._collect_metrics(chunk.metrics)
                    
                    yield chunk
            
            return stream_with_metrics()
        else:
            # Non-streaming response
            response = await inference_provider.infer_async(
                prompt=actual_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                system_prompt=system_prompt,
                **kwargs
            )
            
            # Add prompt metadata to metrics
            response.metrics.prompt_metadata = prompt_metadata
            response.metrics.session_id = session_id
            response.metrics.optimization_data = validated_optimization_data
            
            # Collect metrics
            self._collect_metrics(response.metrics)
            
            # Trigger data collection if optimization_data or project_id is present
            if self.promptlyzer_client and (validated_optimization_data or project_id):
                self.promptlyzer_client.collect_inference_data(
                    prompt=actual_prompt,
                    response=response.content,
                    project_id=project_id,  # Added project_id
                    model=response.model,
                    provider=response.provider,
                    session_id=session_id,
                    optimization_data=validated_optimization_data,
                    metrics={
                        "latency_ms": response.metrics.latency_ms,
                        "tokens": response.metrics.total_tokens,
                        "cost": response.metrics.cost
                    }
                )
            
            return response
    
    def infer(
        self,
        prompt: Union[str, Dict[str, Any]],
        model: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        project_id: Optional[str] = None,
        prompt_name: Optional[str] = None,
        session_id: Optional[str] = None,
        optimization_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[InferenceResponse, Generator[StreamChunk, None, None]]:
        """Perform synchronous inference."""
        if stream:
            # Return a generator for streaming
            return self._stream_sync(
                prompt=prompt,
                model=model,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                project_id=project_id,
                prompt_name=prompt_name,
                session_id=session_id,
                optimization_data=optimization_data,
                **kwargs
            )
        else:
            # Non-streaming case - return InferenceResponse directly
            return _run_async(
                self.infer_async(
                    prompt=prompt,
                    model=model,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                    system_prompt=system_prompt,
                    project_id=project_id,
                    prompt_name=prompt_name,
                    session_id=session_id,
                    optimization_data=optimization_data,
                    **kwargs
                )
            )
    
    def _stream_sync(self, **kwargs) -> Generator[StreamChunk, None, None]:
        """Helper method to handle synchronous streaming."""
        import queue
        import threading
        
        # Create a queue for passing chunks between threads
        chunk_queue = queue.Queue()
        exception = None
        
        async def stream_producer():
            """Produce chunks from async stream."""
            nonlocal exception
            try:
                async for chunk in await self.infer_async(stream=True, **kwargs):
                    chunk_queue.put(chunk)
            except Exception as e:
                exception = e
            finally:
                # Signal end of stream
                chunk_queue.put(None)
        
        # Run async producer in a separate thread
        def run_producer():
            _run_async(stream_producer())
        
        producer_thread = threading.Thread(target=run_producer)
        producer_thread.start()
        
        # Yield chunks as they arrive
        while True:
            chunk = chunk_queue.get()
            if chunk is None:
                # End of stream
                break
            yield chunk
        
        # Wait for producer thread to finish
        producer_thread.join()
        
        # Raise any exception that occurred
        if exception:
            raise exception
    
    def _collect_metrics(self, metrics: InferenceMetrics):
        """Collect metrics for analysis."""
        self.metrics_buffer.append(metrics)
        
        # Track total requests (never resets)
        self.total_requests_count += 1
        
        # Update summary
        provider_summary = self.metrics_summary[metrics.provider]
        provider_summary["total_requests"] += 1
        
        if metrics.success:
            provider_summary["successful_requests"] += 1
            provider_summary["total_cost"] += metrics.cost
            provider_summary["total_tokens"] += metrics.total_tokens
            
            # Update average latency
            total_latency = provider_summary["average_latency_ms"] * (provider_summary["successful_requests"] - 1)
            provider_summary["average_latency_ms"] = (total_latency + metrics.latency_ms) / provider_summary["successful_requests"]
            
            # Update model-specific metrics
            model_summary = provider_summary["models"][metrics.model]
            model_summary["requests"] += 1
            model_summary["cost"] += metrics.cost
            model_summary["tokens"] += metrics.total_tokens
            
            # Update model average latency
            model_total_latency = model_summary["average_latency_ms"] * (model_summary["requests"] - 1)
            model_summary["average_latency_ms"] = (model_total_latency + metrics.latency_ms) / model_summary["requests"]
        else:
            provider_summary["failed_requests"] += 1
        
        # Update uptime percentage
        provider_summary["uptime_percentage"] = (
            provider_summary["successful_requests"] / provider_summary["total_requests"]
        ) * 100
        
        # Adaptive metrics submission logic
        self._check_and_submit_metrics()
    
    def _check_and_submit_metrics(self):
        """
        Automatically submit metrics based on simple triggers.
        
        Rules:
        1. First 5 requests: Send immediately for quick feedback (only for new users)
        2. After that: Batch every 50 requests
        3. Daily: Force send any pending metrics at day change
        """
        buffer_size = len(self.metrics_buffer)
        
        if buffer_size == 0:
            return
        
        # First time check - do this only once
        if not self.first_check_done:
            self.first_check_done = True
            if self.promptlyzer_client:
                try:
                    # Check if there's existing data in cloud
                    cloud_metrics = self.promptlyzer_client.get_inference_metrics(days=30)
                    total_requests = sum(
                        p.get('total_requests', 0) 
                        for p in cloud_metrics.values() 
                        if isinstance(p, dict)
                    )
                    
                    if total_requests > 0:
                        self.has_sent_early_batch = True  # Skip early batch for existing users
                        logger.debug(f"Existing user ({total_requests} requests in cloud), using 50-batch mode")
                    else:
                        self.has_sent_early_batch = False  # New user, will send early batch
                        logger.debug("New user detected, will send early batch")
                except Exception as e:
                    logger.debug(f"Could not check cloud metrics: {e}")
                    self.has_sent_early_batch = False  # Assume new user
            else:
                self.has_sent_early_batch = False  # No client, assume new user
        
        # Submission logic
        should_submit = False
        reason = ""
        
        # Rule 1: First 5 requests - send for quick feedback (new users only)
        if self.has_sent_early_batch == False and buffer_size >= self.early_batch_size:
            should_submit = True
            reason = f"Early batch ({buffer_size} metrics) for new user feedback"
            self.has_sent_early_batch = True
        
        # Rule 2: Regular batch size reached (50 requests)
        elif buffer_size >= self.metrics_batch_size:
            should_submit = True
            reason = f"Batch size reached ({buffer_size} metrics)"
        
        # Rule 3: Daily force send (24 hours passed)
        else:
            time_since_last = datetime.now(timezone.utc) - self.last_metrics_submission
            if time_since_last >= timedelta(hours=24) and buffer_size > 0:
                should_submit = True
                reason = f"Daily submission (24h passed, {buffer_size} metrics pending)"
        
        # Submit if needed
        if should_submit:
            self._submit_metrics(reason)
    
    def _submit_metrics(self, reason: str):
        """Helper method to submit metrics with logging."""
        try:
            logger.debug(f"Submitting metrics: {reason}")
            import asyncio
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.submit_metrics_to_api())
            self.last_metrics_submission = datetime.now(timezone.utc)
        except Exception as e:
            logger.debug(f"Failed to submit metrics: {e}")
            # Optionally save locally if critical
            # self._save_metrics()
    
    def flush_metrics(self, force: bool = False):
        """
        Manually flush metrics buffer to API.
        
        Args:
            force: If True, send even if buffer is small
        """
        if force or len(self.metrics_buffer) > 0:
            try:
                logger.info(f"Manually flushing {len(self.metrics_buffer)} metrics")
                import asyncio
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.submit_metrics_to_api())
                self.last_metrics_submission = datetime.now(timezone.utc)
                return True
            except Exception as e:
                logger.error(f"Failed to flush metrics: {e}")
                self._save_metrics()
                return False
        return True
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        # Convert defaultdict to regular dict for JSON serialization
        summary = {}
        for provider, data in self.metrics_summary.items():
            summary[provider] = {
                **data,
                "models": dict(data["models"])
            }
        return summary
    
    def get_provider_metrics(self, provider: str) -> Dict[str, Any]:
        """Get metrics for a specific provider."""
        return dict(self.metrics_summary.get(provider, {}))
    
    async def submit_metrics_to_api(self):
        """Submit collected metrics to Promptlyzer API."""
        if not self.promptlyzer_client:
            raise ValueError("Promptlyzer client not configured")
        
        if not self.metrics_buffer:
            return
        
        try:
            # Get user context from client
            headers = self.promptlyzer_client.get_headers()
            
            # Prepare metrics data
            metrics_data = {
                "metrics": [m.to_dict() for m in self.metrics_buffer],
                "summary": self.get_metrics_summary(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Submit to API
            response = self.promptlyzer_client._session.post(
                f"{self.promptlyzer_client.api_url}/llm-gateway/metrics",
                headers=headers,
                json=metrics_data
            )
            response.raise_for_status()
            
            # Clear buffer after successful submission
            self.metrics_buffer = []
            
        except Exception as e:
            # If API submission fails, save locally as fallback
            self._save_metrics()
            raise Exception(f"Failed to submit metrics to API: {str(e)}")
    
    def _save_metrics(self):
        """Save metrics to local file (optional backup)."""
        # Only save if explicitly enabled via environment variable
        if os.environ.get("PROMPTLYZER_SAVE_METRICS", "false").lower() != "true":
            return
            
        metrics_data = {
            "buffer": [m.to_dict() for m in self.metrics_buffer],
            "summary": self.get_metrics_summary(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)
    
    def _load_metrics(self):
        """Load existing metrics from file (if enabled and exists)."""
        # Only load if explicitly enabled
        if os.environ.get("PROMPTLYZER_SAVE_METRICS", "false").lower() != "true":
            return
            
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    
                # Restore summary only (no state needed anymore)
                if "summary" in data:
                    for provider, metrics in data["summary"].items():
                        self.metrics_summary[provider].update(metrics)
                        # Convert models back to defaultdict
                        if "models" in metrics:
                            models_dict = defaultdict(lambda: {
                                "requests": 0,
                                "cost": 0.0,
                                "tokens": 0,
                                "average_latency_ms": 0.0
                            })
                            models_dict.update(metrics["models"])
                            self.metrics_summary[provider]["models"] = models_dict
            except Exception as e:
                # If loading fails, start fresh
                logger.debug(f"Failed to load metrics: {e}")
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics_buffer = []
        self.metrics_summary.clear()
        if os.path.exists(self.metrics_file):
            os.remove(self.metrics_file)
    
    async def _infer_via_backend(
        self,
        prompt: Union[str, Dict[str, Any]],
        model: str,
        **kwargs
    ) -> InferenceResponse:
        """
        Perform inference using backend credits system.
        
        Args:
            prompt: The prompt text or dict with project/prompt reference
            model: Model identifier
            **kwargs: Additional parameters
            
        Returns:
            InferenceResponse with generated content and metrics
        """
        if not self.promptlyzer_client:
            raise ValueError("PromptlyzerClient reference required for backend inference")
        
        # Prepare request data
        data = {
            "prompt": prompt,
            "model": model,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens"),
            "system_prompt": kwargs.get("system_prompt"),
            "stream": kwargs.get("stream", False),
            "project_id": kwargs.get("project_id"),
            "session_id": kwargs.get("session_id"),
            "collect_optimization_data": kwargs.get("collect_optimization_data", True),
            "optimization_data": kwargs.get("optimization_data"),
            "additional_params": kwargs.get("additional_params", {})
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        # Check if using external API key
        provider = kwargs.get("provider")
        if provider and provider in self.external_api_keys:
            api_config = self.external_api_keys[provider]
            data["provider"] = provider
            data["provider_api_key"] = api_config["api_key"]
            if api_config.get("base_url"):
                data["provider_base_url"] = api_config["base_url"]
        
        # Make request to backend (url and headers are not needed as _make_request handles them)
        
        start_time = datetime.now()
        
        try:
            response = self.promptlyzer_client._make_request(
                method="POST",
                endpoint="/llm-gateway/inference",
                json=data
            )
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Create InferenceResponse
            metrics = None
            if response.get("usage"):
                usage = response["usage"]
                metrics = InferenceMetrics(
                    provider=response.get("provider", "unknown"),
                    model=response.get("model", model),
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    cost=usage.get("estimated_cost", 0.0),
                    latency_ms=latency_ms,
                    success=True,
                    timestamp=datetime.now(timezone.utc)
                )
            
            return InferenceResponse(
                content=response.get("content", ""),
                model=response.get("model", model),
                provider=response.get("provider", "unknown"),
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Backend inference failed: {str(e)}")
            
            # Check if it's an insufficient credits error (402 status)
            if hasattr(e, 'http_status') and e.http_status == 402:
                # Import locally to avoid circular import
                from ..exceptions import InsufficientCreditsError
                
                # Extract details from error response if available
                details = {}
                if hasattr(e, 'response') and e.response:
                    try:
                        error_data = e.response.json() if hasattr(e.response, 'json') else {}
                        details = error_data.get('detail', {}) if isinstance(error_data.get('detail'), dict) else {}
                    except:
                        pass
                
                raise InsufficientCreditsError(
                    message=details.get('message', "Insufficient credits for this operation"),
                    required_credits=details.get('required_credits'),
                    available_credits=details.get('available_credits'),
                    shortage=details.get('shortage'),
                    http_status=402
                )
            
            # Re-raise other exceptions
            raise
    
    async def estimate_cost(self, model: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Estimate the cost of an inference request.
        
        Args:
            model: Model identifier
            max_tokens: Maximum tokens to generate
            
        Returns:
            Cost estimation including credits required and user balance
        """
        if not self.promptlyzer_client:
            raise ValueError("PromptlyzerClient reference required for cost estimation")
        
        data = {
            "model": model,
            "max_tokens": max_tokens
        }
        
        response = self.promptlyzer_client._make_request(
            method="POST",
            endpoint="/llm-gateway/inference/estimate-cost",
            json=data
        )
        
        return response
    
    async def get_backend_models(self) -> Dict[str, Any]:
        """
        Get available models from backend with pricing information.
        
        Returns:
            Dictionary with models grouped by provider and their pricing
        """
        if not self.promptlyzer_client:
            raise ValueError("PromptlyzerClient reference required")
        
        response = self.promptlyzer_client._make_request(
            method="GET",
            endpoint="/llm-gateway/inference/models"
        )
        
        return response
    
    async def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics from backend.
        
        Args:
            days: Number of days to fetch stats for
            
        Returns:
            Usage statistics including costs, tokens, and request counts
        """
        if not self.promptlyzer_client:
            raise ValueError("PromptlyzerClient reference required")
        
        response = self.promptlyzer_client._make_request(
            method="GET",
            endpoint="/llm-gateway/inference/usage",
            params={"days": days}
        )
        
        return response
    
    # Sync wrappers for new methods
    def estimate_cost_sync(self, model: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Synchronous version of estimate_cost."""
        return _run_async(self.estimate_cost(model, max_tokens))
    
    def get_backend_models_sync(self) -> Dict[str, Any]:
        """Synchronous version of get_backend_models."""
        return _run_async(self.get_backend_models())
    
    def get_usage_stats_sync(self, days: int = 30) -> Dict[str, Any]:
        """Synchronous version of get_usage_stats."""
        return _run_async(self.get_usage_stats(days))