"""
Unit tests for schema generation functionality.
"""

import json
from pathlib import Path

import pytest

from sema4ai_docint.agent_server_client.client import AgentServerClient
from sema4ai_docint.utils import validate_extraction_schema


@pytest.mark.schema_eval
class TestSchemaGeneration:
    """Test schema generation functionality."""

    def test_generate_schema(self, agent_client: AgentServerClient):
        """Test schema generation from document."""

        # Use train_ticket.pdf as the test file
        file_name = "docs/train_ticket.pdf"

        # Generate schema from document
        result = agent_client.generate_schema(file_name)

        # Basic assertions
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("type") == "object"
        assert result.get("properties") is not None

    def test_agent_response_to_error_feedback_in_retry_attempt(
        self, agent_client: AgentServerClient
    ):
        """Test that agent can correct errors when given exact error feedback from retry logic."""

        # Get the path to the test PDF file directly
        doc_path = Path(__file__).parent / "test-data" / "docs" / "train_ticket.pdf"

        # Get images from the PDF
        images = agent_client._pdf_to_images(doc_path)

        # Build chat content step by step with images
        chat_content = []

        # Add initial user request
        chat_content.append(
            {
                "kind": "text",
                "text": (
                    "Please generate a JSON Schema from the document represented by these images. "
                    "Do not include comment characters in the JSONSchema. Do use the 'description' "
                    "field to describe the field."
                ),
            }
        )

        # Add the images from the PDF
        chat_content.extend(images)

        # Simulate bad agent response with JSON syntax errors
        bad_json = """
                    {
            // Defines the structure for a basic train ticket record
            "type": "object",
            "properties": {
                // Unique Passenger Name Record assigned after booking
                "pnr": { "type": "string" },  // used to fetch ticket status later

                // Code representing the train (e.g., 12951 for Rajdhani Express)
                "train_number": { "type": "string" }  // mandatory for identifying the service

                // List of all travelers included in the booking
                "passengers": {
                "type": "array",
                "items": {
                    // Each passenger entry in the list
                    "type": "object",
                    "properties": {
                    "name": { "type": "string" },  // full name as printed on ticket
                    "age": { "type": "integer" }  // used for fare category and berth allocation
                    },
                    "required": ["name", "age"]
                }
                },

                // Total amount charged for the booking including taxes
                "total_fare": { "type": "number"  // expressed in INR
            },
            "required": [
                "pnr",
                "train_number"  // essential for identification
                "passengers",  // must have at least one traveler
                "total_fare"
            ]
        """

        # Generate error feedback as retry logic would
        try:
            json.loads(bad_json)
        except json.JSONDecodeError as e:
            error_feedback = (
                f"Previous response was not valid JSON. Error: {e!s}. Please "
                f"provide valid JSON without markdown formatting."
            )

        # Add error feedback to chat
        chat_content.append({"kind": "text", "text": error_feedback})

        # Send chat with error feedback
        payload = {
            "prompt": {
                "messages": [{"role": "user", "content": chat_content}],
                "tools": [],
                "temperature": 0.7,
                "max_output_tokens": 10240,
            },
        }

        response = agent_client.transport.prompts_generate(payload)

        # Extract and clean response
        from sema4ai_docint.agent_server_client.client import _trim_json_markup

        response_text = agent_client.extract_text_content(response)
        clean_text = _trim_json_markup(response_text)

        # Verify agent corrected the error
        try:
            schema = json.loads(clean_text)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"Agent failed to correct JSON error. Response: {clean_text[:200]}... Error: {e}"
            )

        # validate_extraction_schema will raise an error if the schema is invalid
        _ = validate_extraction_schema(schema)
