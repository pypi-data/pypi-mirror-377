import json
import re
from collections.abc import Callable
from typing import Any


def normalize_name(name: str) -> str:
    """Normalize name by removing special characters, replacing spaces with underscores,
    and converting to lowercase.

    Args:
        name: The name to normalize

    Returns:
        The normalized name
    """
    # Remove special characters (keep only alphanumerics and spaces)
    cleaned = re.sub(r"[^\w\s]", "", name.strip())

    # Replace spaces with underscores and convert to lowercase
    return "_".join(cleaned.split()).lower()


# TODO: This method is being used for data model validation as well. Currently, extraction
# schemas and data model schemas are the same, but they may become separate, at which point
# we need to support both validation concerns.
def validate_extraction_schema(json_schema: str | dict[str, Any]) -> dict[str, Any]:
    """Validates a JSON schema for use with Reducto as an extraction schema.

    Args:
        json_schema: The JSON schema to validate

    Returns:
        The parsed schema

    Raises:
        Exception: If the schema is invalid or not compatible with Reducto
    """
    from jsonschema.validators import validator_for

    if isinstance(json_schema, str):
        parsed_schema = json.loads(json_schema)
    else:
        parsed_schema = json_schema

    # Get the appropriate validator for this schema (note that usually we won't get a schema
    # with a $schema keyword, so we will likely be using the default validator)
    # TODO: Reducto's extraction schema is a subset of JSONschema, be more specific.
    validator_class = validator_for(parsed_schema)
    validator = validator_class(parsed_schema)

    # Validate that the schema itself is valid according to JSON Schema specification
    validator.check_schema(parsed_schema)

    # Reducto requires schemas to be of type "object"
    schema_type = parsed_schema.get("type")
    if schema_type != "object":
        raise ValueError(f"Schema must be of type 'object', got type '{schema_type}'")
    properties = parsed_schema.get("properties")
    if properties is None or not isinstance(properties, dict):
        raise ValueError("Schema must have a non-null 'properties' field of type 'object'")

    return parsed_schema


def _filter_jsonschema(schema: Any, key_filter: Callable[[str], bool]) -> Any:
    """Filter a JSON schema by removing keys that match the filter function.

    Args:
        schema: The JSON schema to filter
        key_filter: Keys matching the filter will be removed from the schema

    Returns:
        The filtered schema
    """
    if not isinstance(schema, dict):
        return schema

    result = {}
    for key, value in schema.items():
        if key_filter(key):
            continue

        if isinstance(value, dict):
            result[key] = _filter_jsonschema(value, key_filter)
        elif isinstance(value, list):
            result[key] = [
                _filter_jsonschema(item, key_filter) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result


def _replace_jsonschema_values(schema: Any, replacements: dict[str, str]) -> Any:
    """Replace values in a JSON schema with values from different keys at the same level.

    Args:
        schema: The JSON schema to modify
        replacements: Dictionary mapping target_key -> source_key for replacements

    Returns:
        The schema with replaced values
    """
    if not isinstance(schema, dict):
        return schema

    result = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            result[key] = _replace_jsonschema_values(value, replacements)
        elif isinstance(value, list):
            result[key] = [
                _replace_jsonschema_values(item, replacements) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    # Apply replacements at this level. If the replacement doesn't exist, we leave
    # the original value.
    for target_key, source_key in replacements.items():
        if target_key in result and source_key in result:
            result[target_key] = result[source_key]

    return result
