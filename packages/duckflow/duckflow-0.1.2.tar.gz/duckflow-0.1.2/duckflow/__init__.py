"""
DuckFlow 🦆
Composable pipelines ("flocks") built from modular processing units ("ducks").
"""

from .core.runner import main as run_cli
from .core.duck import Duck
from .core.flock import run_flock, load_ducks, load_flock_defs
from .core.registry import ServiceRegistry
from .core.settings import load_settings
from .handlers import NODE_FUNCTIONS

__all__ = [
    "Duck",
    "run_flock",
    "load_ducks",
    "load_flock_defs",
    "ServiceRegistry",
    "load_settings",
    "NODE_FUNCTIONS",
    "run_cli",
]
