"""
Base Integration class for all enrichment integrations.

Provides shared infrastructure:
- DatagenClient initialization
- Input validation
- Error handling
- Contract enforcement via ABC
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None
from typing import TYPE_CHECKING

# Load environment once at module level
env_path = Path(__file__).parent.parent.parent / ".env"
if load_dotenv:
    load_dotenv(env_path)

if TYPE_CHECKING:
    from datagen_sdk import DatagenClient


class Integration(ABC):
    """
    Base class for all integrations.

    Subclasses must implement:
    - input_cols: List of required input columns
    - output_cols: List of columns this integration produces
    - _enrich(row): Core enrichment logic
    """

    def __init__(self):
        """Initialize client lazily (lets non-execution commands work without deps)."""
        self._client = None

    @property
    def client(self) -> "DatagenClient":
        if self._client is None:
            if not os.getenv("DATAGEN_API_KEY"):
                raise RuntimeError("DATAGEN_API_KEY not set")
            try:
                from datagen_sdk import DatagenClient
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "datagen_sdk is not installed. Install dependencies (e.g., pip install datagen-sdk) "
                    "or run in the repo's configured environment."
                ) from e
            self._client = DatagenClient()
        return self._client

    @property
    @abstractmethod
    def input_cols(self) -> list[str]:
        """Columns required as input."""
        pass

    @property
    @abstractmethod
    def output_cols(self) -> list[str]:
        """Columns produced as output."""
        pass

    @property
    def description(self) -> str:
        """Human-readable description of what this integration does."""
        return self.__doc__ or "No description"

    @abstractmethod
    def _enrich(self, row: dict) -> tuple[dict, str]:
        """
        Core enrichment logic. Implement in subclass.

        Args:
            row: Dictionary with input columns

        Returns:
            (enriched_fields, error) tuple:
            - Success: ({"col": "value"}, "")
            - Failure: ({}, "error message")
        """
        pass

    def enrich(self, row: dict) -> tuple[dict, str]:
        """
        Public enrichment method with validation.

        Validates input columns exist before calling _enrich().
        """
        # Validate required inputs
        missing = [col for col in self.input_cols if not row.get(col)]
        if missing:
            return {}, f"missing required columns: {', '.join(missing)}"

        # Call subclass implementation
        try:
            return self._enrich(row)
        except Exception as e:
            # Wrap unexpected errors
            return {}, f"{self.__class__.__name__} error: {str(e)}"
