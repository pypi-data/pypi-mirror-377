import io
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any, BinaryIO, cast

import httpx
from reducto import Reducto
from reducto.types import ExtractResponse, ParseResponse, SplitCategory, SplitResponse
from reducto.types.job_get_response import Result

from sema4ai_docint.logging import logger

from .client import ExtractionClient
from .exceptions import (
    ExtractFailedError,
    UploadForbiddenError,
    UploadMissingFileIdError,
    UploadMissingPresignedUrlError,
    UploadPresignRequestError,
    UploadPutError,
)


class SyncExtractionClient(ExtractionClient):
    """Synchronous Client for extracting documents using Reducto.

    This implementation uses the synchronous Reducto client to upload and process documents.
    However, we use their Job API to poll for job completion rather than blocking on the
    HTTP calls.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        disable_ssl_verification: bool = False,
    ):
        """Initialize the Reducto client.

        Args:
            api_key: Sema4.ai API key.
        """
        if not base_url:
            base_url = super().SEMA4_REDUCTO_ENDPOINT

        self._client = SyncExtractionClient._new_reducto_client(
            api_key,
            base_url=base_url,
            disable_ssl_verification=disable_ssl_verification,
        )
        self.base_url = base_url
        self.disable_ssl_verification = disable_ssl_verification

    # TODO: Fix lint issues in this function
    def upload(  # noqa: C901, PLR0915, PLR0912
        self, document: Path | bytes | BinaryIO, *, content_length: int | None = None
    ) -> str:
        """Upload a document to Reducto.

        Args:
            document: A `Path` to a local file, raw `bytes`, or a binary file-like object to upload.
            content_length: Optional explicit content length. If not provided, it will be
                inferred when possible.

        Returns:
            The file ID of the uploaded document.
        """
        # Nb. Previous, we would upload direct to Reducto if it was less than 8MB.
        # However, the backend.sema4.ai API Gateway is mangling the Content-Type (or similar).
        # Now, force the presigned-url regardless of the file size to avoid this.

        # use the presigned url to upload the file
        try:
            upload_resp = self.client._client.post(
                f"{self.base_url}/upload",
                headers=self.client._client.headers,
            )
        except httpx.HTTPError as exc:
            logger.error(f"Presign request failed: {exc}")
            raise UploadPresignRequestError(
                "Failed to request presigned upload URL.",
            ) from exc

        # raise a well-formed exception if the upload failed with http/403
        if upload_resp.status_code == httpx.codes.FORBIDDEN:
            logger.error(f"File upload failed with http/403: {upload_resp}")
            raise UploadForbiddenError(
                "File upload forbidden (HTTP 403). Check your Sema4.ai API key and permissions."
            )

        # raise an exception if the upload failed for any other reason
        try:
            upload_resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else None
            logger.error(f"Presign request returned error status: {status}")
            raise UploadPresignRequestError(
                "Failed to request presigned upload URL.", status_code=status
            ) from exc

        try:
            resp = upload_resp.json()
        except Exception as exc:
            logger.error(f"Invalid presign response: {exc}")
            raise UploadPresignRequestError("Failed to parse presign response.") from exc
        # make sure the upload response has the expected fields
        if "presigned_url" not in resp:
            logger.error(f"File upload failed: No presigned URL returned. Response: {upload_resp}")
            raise UploadMissingPresignedUrlError("File upload failed: No presigned URL returned.")
        if "file_id" not in resp:
            logger.error(f"File upload failed: No file ID returned. Response: {upload_resp}")
            raise UploadMissingFileIdError("File upload failed: No file ID returned.")

        # Prepare a stream and content length for upload
        stream: BinaryIO
        length: int | None = content_length

        if isinstance(document, Path):
            stream = open(document, "rb")
            if length is None:
                try:
                    length = document.stat().st_size
                except Exception:
                    length = None
        elif isinstance(document, bytes):
            stream = io.BytesIO(document)
            if length is None:
                length = len(document)
        else:
            # assume file-like BinaryIO
            stream = document
            if length is None:
                # Try to infer length from tell/seek without consuming the stream permanently
                try:
                    current_pos = stream.tell()
                    stream.seek(0, 2)
                    end_pos = stream.tell()
                    stream.seek(current_pos)
                    length = end_pos - current_pos
                except Exception:
                    # As a fallback, read into memory to compute length to avoid chunked upload
                    data = stream.read()
                    stream = io.BytesIO(data)
                    length = len(data)

        # Ensure Content-Length to avoid chunked upload. Use minimal headers for presigned URL.
        headers: dict[str, str] = {}
        if length is not None:
            headers["Content-Length"] = str(length)

        try:
            try:
                put_resp = self.client._client.put(
                    resp["presigned_url"],
                    content=stream,
                    headers=headers,
                )
            except httpx.HTTPError as exc:
                logger.error(f"Upload PUT request failed: {exc}")
                raise UploadPutError("Failed to upload content to presigned URL.") from exc
        finally:
            # Close only if we opened it here (Path or bytes)
            if isinstance(document, Path | bytes):
                try:
                    stream.close()
                except Exception:
                    pass
        try:
            put_resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else None
            logger.error(f"Upload PUT returned error status: {status}")
            raise UploadPutError(
                "Failed to upload content to presigned URL.", status_code=status
            ) from exc

        # Return the file_id
        return resp["file_id"]

    def unwrap(self) -> Reducto:
        """Return the underlying Reducto client.

        Returns:
            The underlying Reducto client.
        """
        return self._client

    def parse(self, document_id: str, config: dict | None = None) -> ParseResponse:
        """Parse a document using Reducto.

        Args:
            document_id: The Reducto file ID of the document to parse.
            config: Optional configuration to override default parse settings

        Returns:
            The parse response from Reducto.
        """
        opts = self.parse_opts(config)

        # log a note about the Reducto extraction configuration we're using
        if opts:
            import pprint

            logger.info(f"Parse config: {pprint.pformat(opts, indent=2)}")

        job_resp = self.client.parse.run_job(
            document_url=document_id,
            **opts,
        )

        resp = self._complete(job_resp.job_id)
        parsed_resp = cast(ParseResponse, resp)
        return ExtractionClient.localize_parse_response(parsed_resp)

    def split(
        self,
        document_id: str,
        split_description: Iterable[SplitCategory],
        split_rules: str | None = None,
        config: dict | None = None,
    ) -> SplitResponse:
        """Split a document using Reducto.

        Args:
            document_id: The Reducto file ID of the document to split.
            split_description: The description of the split to perform.
            split_rules: Optional split rules to use.
            config: Optional configuration to override default split settings

        Returns:
        """
        # Default options
        opts = self.split_opts(config)

        # Set split_descriptions
        opts["split_description"] = list(split_description)
        # Optionally set split_rules
        if split_rules:
            opts["split_rules"] = split_rules

        # log a note about the Reducto split configuration we're using
        if opts:
            import pprint

            logger.info(f"Split config: {pprint.pformat(opts, indent=2)}")

        job_resp = self.client.split.run_job(
            document_url=document_id,
            **opts,
        )

        resp = self._complete(job_resp.job_id)
        return cast(SplitResponse, resp)

    def extract(
        self,
        document_id: str,
        schema: dict,
        system_prompt: str | None = None,
        start_page: int | None = None,
        end_page: int | None = None,
        extraction_config: dict | None = None,
    ) -> ExtractResponse:
        """Extract data from a document using Reducto.

        Args:
            document_id: The Reducto file ID of the document to extract data from.
            schema: The JSON schema for extraction
            system_prompt: Optional custom system prompt for extraction
            start_page: Optional start page for extraction
            end_page: Optional end page for extraction
            extraction_config: Optional configuration to override default extraction settings

        Returns:
            The extraction response from Reducto.
        """
        # leave a hint about the extraction system prompt in-use
        if system_prompt:
            logger.info(f"using custom prompt for extraction: '{system_prompt}'")
        else:
            logger.info("using standard prompt for extraction")

        opts = self.extract_opts(
            schema,
            (
                ExtractionClient.DEFAULT_EXTRACT_SYSTEM_PROMPT
                if system_prompt is None
                else system_prompt
            ),
            start_page=start_page,
            end_page=end_page,
            extraction_config=extraction_config,
        )

        # log a note about the Reducto extraction configuration we're using
        if opts:
            import pprint

            logger.info(f"Extraction config: {pprint.pformat(opts, indent=2)}")

        job_resp = self.client.extract.run_job(
            document_url=document_id,
            **opts,
        )

        resp = self._complete(job_resp.job_id)
        return cast(ExtractResponse, resp)

    # reducto's Result type appears to not be exported for us to use.
    def _complete(self, job_id: str) -> Result:
        while True:
            job_resp = self.client.job.get(
                job_id=job_id,
            )
            match job_resp.status:
                case "Completed":
                    return job_resp.result
                case "Failed":
                    logger.error(f"Extract job failed: {job_resp.reason}")
                    raise ExtractFailedError(
                        f"Extract job failed: {job_resp.reason}", reason=job_resp.reason
                    )
                case "Pending":
                    time.sleep(3)
                case "Idle":
                    time.sleep(3)
                case _:
                    raise Exception(f"Unknown job status: {job_resp.status}")

    def extract_content(
        self,
        file_path: Path,
        extraction_schema: dict[str, Any],
        data_model_prompt: str | None = None,
        extraction_config: dict[str, Any] | None = None,
        document_layout_prompt: str | None = None,
        start_page: int | None = None,
        end_page: int | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Extract data from a document using Reducto.

        Note: citations are enabled by default, to disable them, provide an extraction_config
        with generate_citations set to False.

        Args:
            extraction_schema: Extraction schema to use for processing (string or
                ExtractionSchema dict).
                This defines the structure for extracting data from the document.
                Should contain JSONSchema properties like 'type', 'properties', 'required'.
            data_model_prompt: Optional system prompt for processing
            extraction_config: Optional extraction configuration for processing
            document_layout_prompt: Optional system prompt for layout processing
            start_page: Optional start page for extraction (1-indexed)
            end_page: Optional end page for extraction (1-indexed)
        """
        file_id = self.upload(file_path)

        # Parse the document
        parse_resp = self.parse(file_id, config=extraction_config)
        job_id = parse_resp.job_id

        # Extract content using the schema
        system_prompt = ExtractionClient.DEFAULT_EXTRACT_SYSTEM_PROMPT
        if data_model_prompt:
            system_prompt += "\n" + data_model_prompt
        if document_layout_prompt:
            system_prompt += "\n" + document_layout_prompt

        logger.info(f"System prompt: {system_prompt}")
        # Extract content with optional configuration
        extract_resp = self.extract(
            f"jobid://{job_id}",
            extraction_schema,
            system_prompt=system_prompt,
            start_page=start_page,
            end_page=end_page,
            extraction_config=extraction_config,
        )

        # Get the extracted results
        results = extract_resp.result
        if not results:
            raise ValueError("No results from extraction")

        citations: dict[str, Any] = {}
        if extract_resp.citations:
            citations = extract_resp.citations[0]  # type: ignore

        logger.info("Content extracted successfully")
        return results[0], citations  # type: ignore
