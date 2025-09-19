import json
import warnings
from pathlib import Path

from reducto import Reducto
from typing_extensions import Any

from sema4ai_docint.extraction.reducto.sync import SyncExtractionClient
from sema4ai_docint.models.extraction import ExtractionResult
from sema4ai_docint.services.exceptions import ExtractionServiceError


class _ExtractionService:
    """Service meant to encapsulate more extraction clients with different capabilities
    and custom logic but also provide access to the underlying clients."""

    def __init__(self, sema4_api_key: str, disable_ssl_verification: bool = False):
        self._sema4_api_key = sema4_api_key
        self._reducto_client = SyncExtractionClient(
            api_key=sema4_api_key,
            disable_ssl_verification=disable_ssl_verification,
        )

    @property
    def reducto(self) -> Reducto:
        """The underlying reducto client"""
        return self._reducto_client.unwrap()

    def extract(
        self,
        file_path: Path,
        extraction_schema: str | dict[str, Any],
        data_model_prompt: str | None = None,
        extraction_config: dict[str, Any] | None = None,
        document_layout_prompt: str | None = None,
        start_page: int | None = None,
        end_page: int | None = None,
    ) -> dict[str, Any]:
        """Extract data from a document"""
        warnings.warn(
            "extract() is deprecated, use extract_details() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        resp = self.extract_details(
            file_path,
            extraction_schema,
            data_model_prompt,
            extraction_config,
            document_layout_prompt,
            start_page,
            end_page,
        )
        return resp.results

    def extract_details(
        self,
        file_path: Path,
        extraction_schema: str | dict[str, Any],
        data_model_prompt: str | None = None,
        extraction_config: dict[str, Any] | None = None,
        document_layout_prompt: str | None = None,
        start_page: int | None = None,
        end_page: int | None = None,
    ) -> ExtractionResult:
        """Extract data from a document, including additional metadata from the extraction."""
        try:
            # TODO the LLM sometimes wants to pass in the name of the layout rather than
            # the actual json schema.
            # do we need to gracefully handle this?
            if isinstance(extraction_schema, str):
                parsed_schema = json.loads(extraction_schema)
            else:
                parsed_schema = extraction_schema

            result, citations = self._reducto_client.extract_content(
                file_path,
                parsed_schema,
                data_model_prompt,
                extraction_config,
                document_layout_prompt,
                start_page,
                end_page,
            )
            return ExtractionResult(results=result, citations=citations)
        except Exception as e:
            raise ExtractionServiceError(f"Error extracting document: {e}") from e
