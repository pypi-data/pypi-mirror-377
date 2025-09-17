"""
LangGraph framework instrumentor.

This module provides instrumentation for LangGraph nodes to track their execution
within the runtime system.
"""

import functools
import importlib
from typing import Any, Dict, Optional, Callable
import uuid

from .interfaces import FrameworkInstrumentor, ExecutionTracker
from .context import get_current_context


class LangGraphInstrumentor(FrameworkInstrumentor):
    """Instrumentor for LangGraph framework."""

    def __init__(self):
        self._tracker: Optional[ExecutionTracker] = None
        self._original_functions: Dict[str, Callable] = {}
        self._installed = False

    @property
    def framework_name(self) -> str:
        """Name of the framework this instrumentor handles."""
        return "langgraph"

    def install(self, tracker: ExecutionTracker) -> None:
        """Install instrumentation hooks for LangGraph."""
        if self._installed:
            return

        self._tracker = tracker

        try:
            # Try to import LangGraph modules - handle different import paths
            langgraph_core = None
            try:
                langgraph_core = importlib.import_module("langgraph.graph")
            except ImportError:
                # Try alternative import path
                langgraph_core = importlib.import_module("langgraph")

            # Instrument CompiledStateGraph.invoke if it exists
            if hasattr(langgraph_core, "CompiledStateGraph"):
                self._instrument_compiled_graph(langgraph_core.CompiledStateGraph)

            # Also try the state module which may have the compiled graph
            try:
                langgraph_state = importlib.import_module("langgraph.graph.state")
                if hasattr(langgraph_state, "CompiledStateGraph"):
                    self._instrument_compiled_graph(langgraph_state.CompiledStateGraph)
            except ImportError:
                pass

            # Try to instrument other common LangGraph classes
            try:
                langgraph_pregel = importlib.import_module("langgraph.pregel")
                if hasattr(langgraph_pregel, "Pregel"):
                    self._instrument_pregel(langgraph_pregel.Pregel)
            except ImportError:
                pass

            # Try to instrument node execution at a deeper level
            try:
                self._instrument_node_functions()
            except Exception as e:
                print(f"[RUNTIME] Could not instrument individual nodes: {e}")

            self._installed = True
            print(f"[RUNTIME] Installed {self.framework_name} instrumentation")

        except ImportError:
            print(f"[RUNTIME] LangGraph not found, skipping instrumentation")

    def uninstall(self) -> None:
        """Remove instrumentation hooks for LangGraph."""
        if not self._installed:
            return

        # Restore original functions
        for module_attr, original_func in self._original_functions.items():
            module_name, attr_name = module_attr.rsplit(".", 1)
            try:
                module = importlib.import_module(module_name)
                setattr(module, attr_name, original_func)
            except (ImportError, AttributeError):
                pass

        self._original_functions.clear()
        self._tracker = None
        self._installed = False
        print(f"[RUNTIME] Uninstalled {self.framework_name} instrumentation")

    def is_installed(self) -> bool:
        """Check if instrumentation is currently installed."""
        return self._installed

    def _instrument_compiled_graph(self, compiled_graph_class: type) -> None:
        """Instrument CompiledStateGraph class methods."""
        # Instrument invoke method
        if hasattr(compiled_graph_class, "invoke"):
            original_invoke = compiled_graph_class.invoke
            class_name = compiled_graph_class.__name__
            self._original_functions[f"langgraph.graph.{class_name}.invoke"] = (
                original_invoke
            )

            # Create a closure that captures the instrumentor instance
            instrumentor = self

            def instrumented_invoke(graph_instance, *args, **kwargs):
                return instrumentor._instrument_node_execution(
                    original_invoke,
                    graph_instance,
                    "invoke",
                    f"{class_name}.invoke",
                    *args,
                    **kwargs,
                )

            compiled_graph_class.invoke = instrumented_invoke

        # Instrument stream method if it exists
        if hasattr(compiled_graph_class, "stream"):
            original_stream = compiled_graph_class.stream
            class_name = compiled_graph_class.__name__
            self._original_functions[f"langgraph.graph.{class_name}.stream"] = (
                original_stream
            )

            # Create a closure that captures the instrumentor instance
            instrumentor = self

            def instrumented_stream(graph_instance, *args, **kwargs):
                return instrumentor._instrument_node_execution(
                    original_stream,
                    graph_instance,
                    "stream",
                    f"{class_name}.stream",
                    *args,
                    **kwargs,
                )

            compiled_graph_class.stream = instrumented_stream

    def _instrument_pregel(self, pregel_class: type) -> None:
        """Instrument Pregel class methods."""
        # Instrument invoke method
        if hasattr(pregel_class, "invoke"):
            original_invoke = pregel_class.invoke
            self._original_functions["langgraph.pregel.Pregel.invoke"] = original_invoke

            # Create a closure that captures the instrumentor instance
            instrumentor = self

            def instrumented_invoke(pregel_instance, *args, **kwargs):
                return instrumentor._instrument_node_execution(
                    original_invoke,
                    pregel_instance,
                    "invoke",
                    "Pregel.invoke",
                    *args,
                    **kwargs,
                )

            pregel_class.invoke = instrumented_invoke

    def _instrument_node_functions(self) -> None:
        """Try to instrument individual node functions by hooking into common execution patterns."""
        try:
            # Try to hook into the node execution mechanism
            langgraph_constants = importlib.import_module("langgraph.constants")
            if hasattr(langgraph_constants, "INVOKE"):
                # This is where individual node functions get called
                print("[LANGGRAPH] Found langgraph constants for node instrumentation")
        except ImportError:
            pass

        # Alternative: try to hook into the runnable interface that nodes often use
        try:
            langchain_core = importlib.import_module("langchain_core.runnables")
            if hasattr(langchain_core, "Runnable"):
                # Many LangGraph nodes inherit from Runnable
                self._instrument_runnable_invoke(langchain_core.Runnable)
        except ImportError:
            pass

    def _instrument_runnable_invoke(self, runnable_class: type) -> None:
        """Instrument Runnable.invoke to catch individual node executions."""
        if hasattr(runnable_class, "invoke"):
            original_invoke = runnable_class.invoke
            self._original_functions["langchain_core.runnables.Runnable.invoke"] = (
                original_invoke
            )

            instrumentor = self

            def instrumented_runnable_invoke(runnable_instance, *args, **kwargs):
                # Get the function name from the runnable instance
                node_name = (
                    getattr(runnable_instance, "name", None)
                    or getattr(
                        runnable_instance, "__class__", type(runnable_instance)
                    ).__name__
                )

                return instrumentor._instrument_node_execution(
                    original_invoke,
                    runnable_instance,
                    "invoke",
                    f"Node.{node_name}",
                    *args,
                    **kwargs,
                )

            runnable_class.invoke = instrumented_runnable_invoke

    def _instrument_node_execution(
        self,
        original_func: Callable,
        instance: Any,
        method_name: str,
        node_name: str,
        *args,
        **kwargs,
    ) -> Any:
        """Wrap a node execution with tracking."""
        # Only track if we have an active request context
        context = get_current_context()
        if not context or not self._tracker:
            return original_func(instance, *args, **kwargs)

        # Generate a unique node ID for this execution
        node_id = str(uuid.uuid4())

        # Extract inputs for tracking - capture more detail
        inputs = {}
        if args:
            # Convert args to serializable format for logging
            serialized_args = []
            for arg in args:
                try:
                    if isinstance(arg, (str, int, float, bool, list, dict)):
                        serialized_args.append(arg)
                    else:
                        serialized_args.append(str(arg)[:200])  # Truncate long objects
                except:
                    serialized_args.append("<unserializable>")
            inputs["args"] = serialized_args
        if kwargs:
            # Convert kwargs to serializable format
            serialized_kwargs = {}
            for k, v in kwargs.items():
                try:
                    if isinstance(v, (str, int, float, bool, list, dict)):
                        serialized_kwargs[k] = v
                    else:
                        serialized_kwargs[k] = str(v)[:200]  # Truncate long objects
                except:
                    serialized_kwargs[k] = "<unserializable>"
            inputs["kwargs"] = serialized_kwargs

        print(f"[LANGGRAPH] Starting node: {node_name}")
        print(f"[LANGGRAPH] Node inputs: {inputs}")

        # Start tracking with timestamp
        import time

        start_time = time.time()

        execution = self._tracker.start_node_execution(
            node_id=node_id,
            node_name=node_name,
            framework=self.framework_name,
            inputs=inputs,
            metadata={
                "method": method_name,
                "class": instance.__class__.__name__,
                "start_time": start_time,
            },
        )

        try:
            # Execute the original function
            result = original_func(instance, *args, **kwargs)

            # Calculate latency
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Track successful completion with detailed outputs
            outputs = None
            if result:
                try:
                    if isinstance(result, (str, int, float, bool, list, dict)):
                        outputs = {"result": result}
                    else:
                        outputs = {
                            "result": str(result)[:500]
                        }  # More detail for outputs
                except:
                    outputs = {"result": "<unserializable>"}

            print(f"[LANGGRAPH] Completed node: {node_name} ({latency_ms:.1f}ms)")
            print(f"[LANGGRAPH] Node outputs: {outputs}")

            self._tracker.end_node_execution(execution, outputs=outputs)

            return result

        except Exception as e:
            # Calculate latency for error case too
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            print(
                f"[LANGGRAPH] ERROR in node: {node_name} ({latency_ms:.1f}ms) - {str(e)}"
            )

            # Track error
            self._tracker.end_node_execution(execution, error=str(e))
            raise
