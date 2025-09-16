import importlib, sys as _sys

# Point 'trajectory' at the real package 'judgeval'
_mod = importlib.import_module("judgeval")

# Make 'import trajectory' return the same module object as 'judgeval'
_sys.modules[__name__] = _mod

# Ensure subpackages like 'trajectory.common' resolve to 'judgeval.common'
def __getattr__(name):
    m = importlib.import_module(f"judgeval.{name}")
    _sys.modules[f"{__name__}.{name}"] = m
    return m

# Import key components that should be publicly accessible
from judgeval.clients import client, together_client
from judgeval.judgment_client import JudgmentClient
from judgeval.common.tracer import Tracer, wrap
from judgeval.version_check import check_latest_version

# Preferred public alias
TrajectoryClient = JudgmentClient

check_latest_version()

__all__ = [
    # Clients
    "client",
    "together_client",
    # Tracing
    "Tracer",
    "wrap",
    # Preferred public name
    "TrajectoryClient",
    # Backward-compat
    "JudgmentClient",
]
