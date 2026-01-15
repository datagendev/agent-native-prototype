"""
Primitive: Extract Structured

Extract structured data from text using a schema.
Uses AI to parse unstructured text into defined fields.

This is a TRUE primitive - works with any schema, any text.
"""

import json
import os
from pydantic import BaseModel, Field, create_model
from openai import OpenAI
import instructor
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from .base import Primitive, register_primitive


@register_primitive
class ExtractStructured(Primitive):
    """Extract structured data from text using a provided schema."""

    name = "extract_structured"
    description = "Parse unstructured text into structured data based on a schema"

    input_schema = {
        "text": {
            "type": "string",
            "description": "The unstructured text to parse",
            "required": True
        },
        "schema": {
            "type": "object",
            "description": "Schema defining fields to extract. Keys are field names, values are {type, description}",
            "required": True
        },
        "context": {
            "type": "string",
            "description": "Optional context to help extraction",
            "required": False
        }
    }

    output_schema = {
        "extracted": {
            "type": "object",
            "description": "Extracted data matching the input schema"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        text = inputs["text"]
        schema = inputs["schema"]
        context = inputs.get("context", "")

        if not text or not text.strip():
            return {}, "empty text"

        if not schema:
            return {}, "empty schema"

        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {}, "OPENAI_API_KEY not set in .env"

        try:
            # Create OpenAI client with instructor
            client = instructor.from_openai(OpenAI(api_key=api_key))

            # Build dynamic Pydantic model from schema
            fields = {}
            for field_name, field_def in schema.items():
                field_type = field_def.get("type", "string")
                field_desc = field_def.get("description", field_name)

                # Map string types to Python types
                if field_type == "integer":
                    python_type = int
                elif field_type == "number":
                    python_type = float
                elif field_type == "boolean":
                    # Boolean should not be nullable for proper extraction
                    python_type = bool
                    fields[field_name] = (python_type, Field(description=field_desc))
                    continue
                else:
                    python_type = str

                # Non-boolean fields are optional (nullable)
                fields[field_name] = (python_type | None, Field(default=None, description=field_desc))

            # Create dynamic Pydantic model
            ExtractionModel = create_model('ExtractionModel', **fields)

            # Build prompt
            prompt = f"""Extract the following information from the text below.
If a field cannot be found, return null for that field.

{f"Context: {context}" if context else ""}

Text:
{text}"""

            # Use instructor to extract structured data
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=ExtractionModel,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            # Convert Pydantic model to dict
            extracted = response.model_dump()

            return {"extracted": extracted}, ""

        except Exception as e:
            return {}, f"extraction failed: {str(e)}"


# Module-level instance for convenient imports
extract_structured = ExtractStructured()
