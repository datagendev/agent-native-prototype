"""
Primitives: Atomic enrichment capabilities.

Primitives are generic, reusable operations that don't know about specific columns.
They are composed by Graphs to create enrichment workflows.

Usage:
    from primitives import web_research, extract_structured, linkedin_profile

    # Call directly
    result, err = web_research(query="Who is the CEO of acme.com?")
    if err:
        print(f"Error: {err}")
    else:
        print(result["result"])

Available Primitives:
    - web_research: Generic web research on any query
    - extract_structured: Parse text into structured data using schema
    - linkedin_profile: Fetch LinkedIn profile data
    - linkedin_posts: Fetch posts from LinkedIn profile
    - filter_by: Filter array by keywords
    - aggregate: Aggregate array into metrics
"""

from .base import Primitive, Graph, PRIMITIVES, register_primitive, get_client

# Import primitives (they self-register via @register_primitive decorator)
from .web_research import web_research, WebResearch
from .extract_structured import extract_structured, ExtractStructured
from .linkedin_profile import linkedin_profile, LinkedInProfile
from .linkedin_posts import linkedin_posts, LinkedInPosts
from .linkedin_search import linkedin_search, LinkedInSearch
from .filter_by import filter_by, FilterBy
from .aggregate import aggregate, Aggregate

__all__ = [
    # Base classes
    "Primitive",
    "Graph",
    "PRIMITIVES",
    "register_primitive",
    "get_client",

    # Primitive instances (for direct use)
    "web_research",
    "extract_structured",
    "linkedin_profile",
    "linkedin_posts",
    "linkedin_search",
    "filter_by",
    "aggregate",

    # Primitive classes (for subclassing)
    "WebResearch",
    "ExtractStructured",
    "LinkedInProfile",
    "LinkedInPosts",
    "LinkedInSearch",
    "FilterBy",
    "Aggregate",
]


def list_primitives() -> dict[str, dict]:
    """List all available primitives with their schemas."""
    result = {}
    for name, prim in PRIMITIVES.items():
        result[name] = {
            "description": prim.description,
            "input_schema": prim.input_schema,
            "output_schema": prim.output_schema
        }
    return result


def get_primitive(name: str) -> Primitive | None:
    """Get a primitive by name."""
    return PRIMITIVES.get(name)
