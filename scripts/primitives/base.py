"""
Base classes for the enrichment system.

Two types of components:
1. Primitive - Atomic capability (web_research, extract_structured, linkedin_profile)
2. Graph - Composed workflow with declared I/O columns

Primitives are generic and reusable across all lead tables.
Graphs are specific to a lead table and define exact columns.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

# Load environment once at module level
env_path = Path(__file__).parent.parent.parent / ".env"
if load_dotenv:
    load_dotenv(env_path)

if TYPE_CHECKING:
    from datagen_sdk import DatagenClient


# Shared client instance
_client = None


def get_client() -> "DatagenClient":
    """Get or create shared DatagenClient."""
    global _client
    if _client is None:
        if not os.getenv("DATAGEN_API_KEY"):
            raise RuntimeError("DATAGEN_API_KEY not set")
        try:
            from datagen_sdk import DatagenClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "datagen_sdk is not installed. Install dependencies (e.g., pip install datagen-sdk) "
                "or run in the repo's configured environment."
            ) from e
        _client = DatagenClient()
    return _client


class Primitive(ABC):
    """
    Base class for atomic enrichment primitives.

    Primitives are generic capabilities that don't know about specific columns.
    They work with named parameters and return structured results.

    Example:
        class WebResearch(Primitive):
            name = "web_research"
            input_schema = {"query": {"type": "string"}}
            output_schema = {"result": {"type": "string"}}

            def run(self, **inputs) -> tuple[dict, str]:
                result = self.client.execute_tool("chatgpt_webresearch", {"query": inputs["query"]})
                return {"result": result.get("answer", "")}, ""
    """

    name: str = ""
    description: str = ""
    input_schema: dict[str, dict] = {}
    output_schema: dict[str, dict] = {}

    def __init__(self):
        self._client = None

    @property
    def client(self) -> "DatagenClient":
        if self._client is None:
            self._client = get_client()
        return self._client

    @abstractmethod
    def run(self, **inputs) -> tuple[dict, str]:
        """
        Execute the primitive.

        Args:
            **inputs: Named parameters matching input_schema

        Returns:
            (result_dict, error_string) tuple:
            - Success: ({"key": "value"}, "")
            - Failure: ({}, "error message")
        """
        pass

    def validate_inputs(self, inputs: dict) -> str | None:
        """Validate inputs against schema. Returns error message or None."""
        for key, schema in self.input_schema.items():
            if key not in inputs:
                if schema.get("required", True):
                    return f"missing required input: {key}"
        return None

    def __call__(self, **inputs) -> tuple[dict, str]:
        """Allow primitives to be called directly: primitive(query="...")"""
        err = self.validate_inputs(inputs)
        if err:
            return {}, err
        try:
            return self.run(**inputs)
        except Exception as e:
            return {}, f"{self.name} error: {str(e)}"


class Graph(ABC):
    """
    Base class for enrichment graphs.

    Graphs compose primitives into workflows with declared I/O columns.
    They are specific to a lead table and define exact column names.

    Example:
        class FindCEO(Graph):
            input_cols = ["company_domain"]
            output_cols = ["ceo_name", "ceo_linkedin_url"]

            def run(self, row: dict) -> tuple[dict, str]:
                research, err = web_research(query=f"Who is CEO of {row['company_domain']}?")
                if err:
                    return {}, err
                # ... more logic
                return {"ceo_name": "...", "ceo_linkedin_url": "..."}, ""
    """

    @property
    @abstractmethod
    def input_cols(self) -> list[str]:
        """Columns required from the source CSV."""
        pass

    @property
    @abstractmethod
    def output_cols(self) -> list[str]:
        """Columns this graph will add to the CSV."""
        pass

    @property
    def description(self) -> str:
        """Human-readable description."""
        return self.__doc__ or self.__class__.__name__

    @abstractmethod
    def run(self, row: dict) -> tuple[dict, str]:
        """
        Execute graph on a single row.

        Args:
            row: Dictionary with input columns from CSV

        Returns:
            (result_dict, error_string) tuple:
            - Success: ({"col": "value", ...}, "")
            - Failure: ({}, "error message")

        Result dict keys MUST match output_cols.
        """
        pass

    def validate_row(self, row: dict) -> str | None:
        """Validate row has required input columns. Returns error or None."""
        missing = [col for col in self.input_cols if not row.get(col)]
        if missing:
            return f"missing columns: {', '.join(missing)}"
        return None

    def __call__(self, row: dict) -> tuple[dict, str]:
        """Allow graphs to be called directly: graph(row)"""
        err = self.validate_row(row)
        if err:
            return {}, err
        try:
            result, err = self.run(row)
            if err:
                return {}, err
            # Validate output matches declared columns
            for col in self.output_cols:
                if col not in result:
                    result[col] = ""  # Fill missing with empty
            return result, ""
        except Exception as e:
            return {}, f"{self.__class__.__name__} error: {str(e)}"

    def preview(self, row: dict) -> str:
        """Generate preview string for auditing."""
        input_vals = {col: row.get(col, "?") for col in self.input_cols}
        return f"""
Graph: {self.__class__.__name__}
Description: {self.description}
Input:  {self.input_cols} = {input_vals}
Output: {self.output_cols}
"""


# Registry for primitives (populated by __init__.py)
PRIMITIVES: dict[str, Primitive] = {}


def register_primitive(cls: type[Primitive]) -> type[Primitive]:
    """Decorator to register a primitive."""
    instance = cls()
    PRIMITIVES[instance.name] = instance
    return cls
