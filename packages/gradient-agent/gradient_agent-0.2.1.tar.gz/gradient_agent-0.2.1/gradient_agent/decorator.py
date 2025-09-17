"""
Gradient entrypoint decorator for creating FastAPI agents.
"""

from __future__ import annotations
import functools
import inspect
from typing import Any, Callable, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
import uvicorn

# Import runtime system
from .runtime.manager import get_runtime_manager


class CompletionResponse(dict):
    """Lightweight response container (dict subclass for FastAPI response_model-free return)."""

    pass


class EntrypointRegistry:
    """Global registry for entrypoint functions."""

    def __init__(self):
        self._function: Optional[Callable] = None
        self._app: Optional[FastAPI] = None

    def register(self, func: Callable) -> FastAPI:
        """Register an entrypoint function and create the FastAPI app."""
        self._function = func

        # Create FastAPI app
        self._app = FastAPI(
            title="Gradient Agent",
            description="AI Agent powered by Gradient",
            version="1.0.0",
        )

        @self._app.post("/completions")
        async def completions(req: Request) -> CompletionResponse:
            """Handle completion requests with minimal assumptions.

            Accepts arbitrary JSON. If "prompt" key exists it is passed as a positional/keyword
            argument only if the user function expects it; otherwise the entire JSON dict is
            passed as a single keyword argument 'data' if present in the function signature.
            No validation or coercion is performed—user code owns input validation.
            """
            try:
                runtime_manager = get_runtime_manager()
                body: Dict[str, Any] = {}
                try:
                    body = await req.json()
                    if not isinstance(body, dict):
                        body = {"value": body}
                except Exception:
                    body = {}

                runtime_manager.start_request(
                    entrypoint_name=func.__name__, inputs=body
                )

                # Build kwargs with zero policy enforcement
                kwargs: Dict[str, Any] = {}
                sig = inspect.signature(func)
                params = sig.parameters
                # If function explicitly wants a 'data' param, give full body
                if "data" in params:
                    kwargs["data"] = body
                # Map any matching top-level keys directly (best-effort)
                for name in body.keys():
                    if name in params and name not in kwargs:
                        kwargs[name] = body[name]
                # If still empty and function expects exactly one param, pass body as that param
                if not kwargs and len(params) == 1:
                    sole = next(iter(params.keys()))
                    kwargs[sole] = body.get(sole, body)

                try:
                    result = func(**kwargs)

                    # Normalize response: allow any type; if not dict or str wrap
                    if isinstance(result, dict):
                        outputs = result
                    elif isinstance(result, str):
                        outputs = {"completion": result}
                    else:
                        outputs = {"completion": str(result)}

                    runtime_manager.end_request(outputs=outputs)
                    return CompletionResponse(outputs)

                except Exception as e:
                    runtime_manager.end_request(error=str(e))
                    raise HTTPException(status_code=500, detail=str(e)) from e

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self._app.get("/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy", "service": "gradient-agent"}

        @self._app.get("/")
        async def root():
            """Root endpoint with basic info."""
            return {
                "service": "gradient-agent",
                "entrypoint": func.__name__ if func else None,
                "endpoints": ["/completions", "/health"],
            }

        return self._app

    def get_app(self) -> FastAPI:
        """Get the registered FastAPI app."""
        if self._app is None:
            raise RuntimeError(
                "No entrypoint function decorated. Use @entrypoint decorator first."
            )
        return self._app


# Global registry instance
_registry = EntrypointRegistry()


def entrypoint(func: Callable) -> Callable:
    """
    Decorator to mark a function as the agent entrypoint.

    The decorated function should accept parameters that match CompletionRequest
    fields and return either a string or a dict with 'completion' key.

    Example:
        @entrypoint
        def my_agent(prompt: str, max_tokens: int = 100) -> str:
            return f"Response to: {prompt}"
    """
    # Register the function and create the app
    _registry.register(func)

    # Return the original function unchanged
    return func


def get_app() -> FastAPI:
    """Get the FastAPI app instance."""
    return _registry.get_app()


def run_server(host: str = "0.0.0.0", port: int = 8080, **kwargs):
    """
    Run the FastAPI server with the decorated entrypoint.

    Args:
        host: Host to bind to
        port: Port to bind to
        **kwargs: Additional arguments to pass to uvicorn.run()
    """
    app = get_app()
    uvicorn.run(app, host=host, port=port, **kwargs)
