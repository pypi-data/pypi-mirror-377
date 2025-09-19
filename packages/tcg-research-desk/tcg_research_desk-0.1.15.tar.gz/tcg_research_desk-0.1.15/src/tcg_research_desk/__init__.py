import importlib.metadata

try:
    __version__ = importlib.metadata.version(__package__)
except importlib.metadata.PackageNotFoundError:
    # This block handles cases where the package is not installed (e.g., during development)
    __version__ = "unknown"

from .process_data import process_mtg_data, load_data
from .ui import MTGAnalyzer, create_dashboard