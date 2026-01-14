"""
Primitive: Email Finder (Direct API Example)

Find email addresses using Hunter.io API with direct HTTP calls.

METADATA:
  name: email_finder
  category: email
  created: 2026-01-14
  api: Hunter.io (direct HTTP, no MCP server)

WHEN TO USE:
  - Need to find professional email addresses
  - Have person name and company domain
  - Validating email existence
  - Keywords: email, contact, find email, email verification

WHEN NOT TO USE:
  - Bulk email finding (use Hunter batch API)
  - Already have the email
  - Need phone numbers (use contact enrichment)
  - Personal emails (this is for professional contacts)

INPUT SCHEMA:
  - domain (string): Company domain (e.g., "stripe.com") [required]
  - first_name (string): Person's first name [optional]
  - last_name (string): Person's last name [optional]

OUTPUT SCHEMA:
  - email (string): Found email address
  - confidence (integer): Confidence score 0-100
  - sources (array): Where the email was found

EXAMPLE USAGE:
  ```python
  from primitives import email_finder

  result, err = email_finder(
      domain="stripe.com",
      first_name="John",
      last_name="Doe"
  )

  if err:
      print(f"Email search failed: {err}")
      return

  print(f"Found: {result['email']}")
  print(f"Confidence: {result['confidence']}%")
  ```

PERFORMANCE:
  - Latency: ~500-1000ms
  - Cost: $0.01 per search (Hunter.io pricing)
  - Rate limits: 100 requests/month (free), 5000/month (paid)
  - API key required: Store in DataGen secrets

This is a TRUE primitive - no hardcoded columns, works with any domain.

API INTEGRATION:
  This primitive uses direct HTTP calls to Hunter.io API.
  Better alternative: Add Hunter.io as MCP server using /build-integrations
"""

import httpx
from .base import Primitive, register_primitive


@register_primitive
class EmailFinder(Primitive):
    """Find email addresses using Hunter.io API."""

    name = "email_finder"
    description = "Find professional email addresses by domain and name"

    input_schema = {
        "domain": {
            "type": "string",
            "description": "Company domain (e.g., 'stripe.com')",
            "required": True
        },
        "first_name": {
            "type": "string",
            "description": "Person's first name",
            "required": False
        },
        "last_name": {
            "type": "string",
            "description": "Person's last name",
            "required": False
        }
    }

    output_schema = {
        "email": {
            "type": "string",
            "description": "Found email address"
        },
        "confidence": {
            "type": "integer",
            "description": "Confidence score 0-100"
        },
        "sources": {
            "type": "array",
            "description": "Where the email was found"
        }
    }

    def _get_api_key(self) -> tuple[str, str]:
        """Get Hunter.io API key from DataGen secrets."""
        try:
            # Note: This assumes you've stored HUNTER_API_KEY in DataGen secrets
            # In actual implementation, use self.client to fetch from secrets
            import os
            api_key = os.getenv("HUNTER_API_KEY")
            if not api_key:
                return "", "HUNTER_API_KEY not found in environment"
            return api_key, ""
        except Exception as e:
            return "", f"failed to get API key: {str(e)}"

    def run(self, **inputs) -> tuple[dict, str]:
        domain = inputs["domain"]

        if not domain or not domain.strip():
            return {}, "empty domain"

        # Get API key
        api_key, err = self._get_api_key()
        if err:
            return {}, err

        # Build API request
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            "domain": domain,
            "api_key": api_key
        }

        # Add optional name parameters
        if "first_name" in inputs and inputs["first_name"]:
            params["first_name"] = inputs["first_name"]
        if "last_name" in inputs and inputs["last_name"]:
            params["last_name"] = inputs["last_name"]

        try:
            # Make HTTP request
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

        except httpx.HTTPStatusError as e:
            return {}, f"API error {e.response.status_code}: {e.response.text}"
        except httpx.RequestError as e:
            return {}, f"request failed: {str(e)}"
        except Exception as e:
            return {}, f"unexpected error: {str(e)}"

        # Parse response
        if "data" not in data:
            return {}, "no data in API response"

        email_data = data["data"]

        email = email_data.get("email", "")
        if not email:
            return {}, "no email found"

        return {
            "email": email,
            "confidence": email_data.get("score", 0),
            "sources": email_data.get("sources", [])
        }, ""


# Module-level instance
email_finder = EmailFinder()
