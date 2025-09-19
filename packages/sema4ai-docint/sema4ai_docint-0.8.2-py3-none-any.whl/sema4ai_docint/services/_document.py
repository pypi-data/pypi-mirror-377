"""
Document service for high-level document operations.
"""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sema4ai.actions.chat import get_file

from sema4ai_docint.extraction.process import (
    ExtractAndTransformContentParams,
    ExtractionSchema,
    TranslationSchema,
    validate_and_parse_schemas,
)
from sema4ai_docint.extraction.reducto.config import ReductoConfig
from sema4ai_docint.extraction.transform import transform_content
from sema4ai_docint.extraction.transform.transform_document_layout import (
    TransformDocumentLayout,
)
from sema4ai_docint.logging import logger
from sema4ai_docint.utils import normalize_name
from sema4ai_docint.validation.models import ValidationRule, ValidationSummary
from sema4ai_docint.validation.validate import validate_document_extraction

from ..models import DataModel, Document, DocumentLayout, initialize_dataserver
from ..models.constants import PROJECT_NAME
from ._context import _DIContext
from .exceptions import DocumentServiceError


@dataclass
class _Experiment:
    """Represents a single processing experiment configuration.

    Attributes:
        name: Human-readable name for the experiment
        extraction_config: Optional Reducto extraction configuration
        user_prompt: Optional user prompt for processing
        layout_prompt: Optional layout prompt for processing
    """

    name: str
    extraction_config: dict[str, Any] | None = None
    user_prompt: str | None = None
    layout_prompt: str | None = None


class _ExperimentResult(BaseModel):
    """Result of running a single experiment.

    Attributes:
        experiment_name: Name of the experiment that was run
        success: Whether the experiment succeeded
        error_message: Error message if experiment failed (None if successful)
        validation_results: Validation results if experiment succeeded
    """

    document: Document | None = None
    experiment_name: str
    success: bool
    error_message: str | None = None
    validation_results: ValidationSummary | None = None


class _ProcessingResponse(BaseModel):
    """Response from document processing with experiments.

    Attributes:
        success: Overall success status
        document: Processed document data
        experiments: List of experiment results showing what was tried
        successful_experiment: Name of the experiment that succeeded (None if all failed)
        total_attempts: Total number of experiments attempted
    """

    success: bool
    document: Document | None = None
    experiments: list[_ExperimentResult]
    successful_experiment: str | None = None
    total_attempts: int


class _DocumentService:
    def __init__(self, context: _DIContext) -> None:
        self._context = context

    def query(self, document_id: str) -> dict[str, Any]:
        """Get document in data model format.

        Args:
            document_id: Document ID to retrieve

        Returns:
            Dict with document data as dict with view names as keys

        Raises:
            DocumentServiceError: If document or data model not found
        """
        document = Document.find_by_id(self._context.datasource, document_id)
        if not document:
            raise DocumentServiceError(f"Document with ID {document_id} not found")

        data_model = DataModel.find_by_name(self._context.datasource, document.data_model)
        if not data_model:
            raise DocumentServiceError(f"Data model with name {document.data_model} not found")

        # Collect all view names from the data model's views
        view_names = []
        if data_model.views:
            for view in data_model.views:
                if isinstance(view, dict) and "name" in view:
                    view_names.append(view["name"])

        if not view_names:
            raise DocumentServiceError(f"No views found for data model {document.data_model}")

        # Initialize the objects in MindsDB (project)
        try:
            initialize_dataserver(PROJECT_NAME, data_model.views)
        except Exception as e:
            raise DocumentServiceError(
                "Failed to create the document intelligence data-server project"
            ) from e

        # Loop over all view names and collect results
        results_dict = {}
        for view_name in view_names:
            sql = f"SELECT * FROM {PROJECT_NAME}.{view_name} where document_id = $document_id"

            results = self._context.datasource.execute_sql(sql, params={"document_id": document_id})
            if results:
                results_dict[view_name] = results.to_table()
            else:
                results_dict[view_name] = None

        return results_dict

    def ingest(
        self,
        file_name: str,
        data_model_name: str,
        layout_name: str,
    ) -> dict[str, Any]:
        """Ingest document into data model using layout.

        This function creates PERSISTENT state by storing the document, extracted content,
        and transformed content in the database.

        Args:
            file_name: PDF file name to process
            data_model_name: Data model name for document
            layout_name: Document layout to use for processing

        Returns:
            Dict with created document containing extracted and transformed content

        Raises:
            DocumentServiceError: If document processing fails
        """
        data_model_name = normalize_name(data_model_name)
        layout_name = normalize_name(layout_name)

        try:
            data_model = DataModel.find_by_name(self._context.datasource, data_model_name)
            if not data_model:
                raise DocumentServiceError(f"Data model {data_model_name} not found")

            layout = DocumentLayout.find_by_name(
                self._context.datasource, data_model_name, layout_name
            )
            if not layout:
                raise DocumentServiceError(f"Document layout does not exist: {layout_name}")

            if not layout.extraction_schema:
                raise DocumentServiceError(f"Layout {layout_name} has no extraction schema")
            if not layout.translation_schema:
                raise DocumentServiceError(f"Layout {layout_name} has no translation schema")

            parsed_extraction_schema, parsed_translation_schema = validate_and_parse_schemas(
                layout.extraction_schema, layout.translation_schema
            )

            response = self._process_with_experiments(
                file_name=file_name,
                data_model=data_model,
                layout_name=layout_name,
                parsed_extraction_schema=parsed_extraction_schema,
                parsed_translation_schema=parsed_translation_schema,
                data_model_prompt=data_model.prompt,
                extraction_config=layout.extraction_config,
                layout_prompt=layout.system_prompt,
            )

            return response.model_dump()

        except Exception as e:
            raise DocumentServiceError(f"Failed to process document: {e!s}") from e

    def extract_with_schema(
        self,
        params: ExtractAndTransformContentParams,
    ) -> dict[str, Any]:
        """Extract, transform, validate content with automatic retry and schema storage.

        This function performs the complete document processing pipeline:
        1. Extract and transform content using provided schemas
        2. Validate the processed document
        3. If validation fails, automatically retry with different configurations
        4. Store successful schemas in database for future use

        Args:
            sema4_api_key: Sema4.ai cloud backend API key
            params: ExtractAndTransformContentParams object containing:
                - file_name: file name to process
                - extraction_schema: Extraction schema as JSON string (must be valid JSON)
                - translation_schema: Translation schema as dict with "rules" key containing
                    array of mapping rules
                - data_model_name: Data model name for document
                - layout_name: Document layout to use for processing
            datasource: Document intelligence data source connection

        Returns:
            Response with created document containing extracted and transformed content,
            validation results, and retry information if applicable.

        Raises:
            DocumentServiceError: If document processing fails after all retry attempts
        """

        data_model = DataModel.find_by_name(self._context.datasource, params.data_model_name)
        if not data_model:
            raise DocumentServiceError(f"Data model {params.data_model_name} not found")

        # Validate and parse schemas
        parsed_extraction_schema, parsed_translation_schema = validate_and_parse_schemas(
            params.extraction_schema, params.translation_schema
        )

        response = self._process_with_experiments(
            file_name=params.file_name,
            data_model=data_model,
            layout_name=params.layout_name,
            parsed_extraction_schema=parsed_extraction_schema,
            parsed_translation_schema=parsed_translation_schema,
            data_model_prompt=data_model.prompt,
            extraction_config=None,
            layout_prompt=None,
        )

        return response.model_dump()

    def validate(self, data_model: DataModel, document_id: str) -> ValidationSummary:
        """Validate a document against quality checks.

        Args:
            data_model_name: The name of the data model
            document_id: The ID of the document to validate
            datasource: The document intelligence data source connection

        Returns:
            Response containing validation results with overall status and rule outcomes

        Raises:
            DocumentServiceError: If data model not found, no quality checks exist,
                project creation fails, or validation fails
        """
        # If there are no quality checks, return success to avoid re-processing at higher levels.
        if not data_model.quality_checks:
            logger.warning(f"No quality checks found for data model {data_model.name}")
            return ValidationSummary(
                overall_status="passed",
                results=[],
                passed=0,
                failed=0,
                errors=0,
            )

        # Initialize the objects in MindsDB (project)
        try:
            initialize_dataserver(PROJECT_NAME, data_model.views)
        except Exception as e:
            raise DocumentServiceError(
                "Failed to create the document intelligence data-server project"
            ) from e

        # Parse quality checks - all stored rules should be valid
        quality_checks = [ValidationRule(**rule) for rule in data_model.quality_checks]

        validation_summary = validate_document_extraction(
            document_id, self._context.datasource, quality_checks
        )

        if validation_summary.overall_status == "failed":
            raise DocumentServiceError(
                f"Document validation encountered errors: {validation_summary.model_dump()}"
            )
        return validation_summary

    def _generate_experiments(
        self,
        initial_extraction_config: dict[str, Any] | None,
        initial_user_prompt: str | None,
        initial_layout_prompt: str | None,
        max_experiments: int = 6,
    ) -> list[_Experiment]:
        """Generate a prioritized list of experiments to try.

        Args:
            initial_extraction_config: The initial extraction config to try first
            initial_user_prompt: The initial user prompt to use
            initial_layout_prompt: The initial layout prompt to use
            max_experiments: Maximum number of experiments to generate

        Returns:
            List of experiments ordered by priority (default config first, then custom configs)
        """
        experiments = []

        experiments.append(
            _Experiment(
                name="default",
                extraction_config=initial_extraction_config,
                user_prompt=initial_user_prompt,
                layout_prompt=initial_layout_prompt,
            )
        )

        custom_configs = ReductoConfig.load_config()
        # Filter out configs that match the initial extraction config (no point retrying
        # with same config)
        filtered_configs = {}
        for config_name, config_data in custom_configs.items():
            if initial_extraction_config and _configs_are_equivalent(
                config_data, initial_extraction_config
            ):
                logger.info(
                    f"Skipping config '{config_name}' as it matches the initial extraction config"
                )
                continue
            filtered_configs[config_name] = config_data

        if not filtered_configs:
            logger.info(
                "All custom configs match the initial extraction config, will only try "
                "default configuration"
            )
            return experiments

        logger.info(
            f"Found {len(filtered_configs)} distinct custom Reducto configs to try "
            f"(filtered from {len(custom_configs)} total configs)"
        )

        # Add filtered custom configs as experiments (limit to max_experiments total)
        remaining_slots = max_experiments - len(experiments)
        for config_name, config_data in list(filtered_configs.items())[:remaining_slots]:
            experiments.append(
                _Experiment(
                    name=f"reducto_{config_name}",
                    extraction_config=config_data,
                    user_prompt=initial_user_prompt,
                    layout_prompt=None,
                )
            )

        return experiments

    def _process_document_with_schemas(
        self,
        file_name: str,
        data_model: DataModel,
        layout_name: str,
        extraction_schema: ExtractionSchema,
        translation_schema: TranslationSchema,
        user_prompt: str | None = None,
        extraction_config: dict[str, Any] | None = None,
        layout_prompt: str | None = None,
    ) -> Document:
        """Helper function to process document with extraction and translation schemas.

        Args:
            file_name: Name of the file
            data_model: Data model for document
            layout_name: Document layout name
            extraction_schema: Parsed extraction schema
            translation_schema: Parsed translation schema
            user_prompt: Optional user prompt for processing
            extraction_config: Optional Reducto extraction configuration
            layout_prompt: Optional layout prompt

        Returns:
            Processed document instance

        Raises:
            DocumentServiceError: If document processing fails
        """
        try:
            # Generate document ID
            pdf_path = get_file(file_name)

            transformer = TransformDocumentLayout()
            document_id = transformer.get_doc_uuid(pdf_path)
            logger.info(f"Generated document ID: {document_id}")

            # Check if document already exists
            document = Document.find_by_id(self._context.datasource, document_id)
            if not document:
                # Create new document
                document = Document(
                    id=document_id,
                    document_name=file_name,
                    data_model=data_model.name,
                    document_layout=layout_name,
                )
                document.insert(self._context.datasource)
            else:
                # Update existing document
                document.document_layout = layout_name
                document.data_model = data_model.name
                document.document_name = file_name
                document.update(self._context.datasource)

            # Extract content using Reducto
            extracted_content = self._context.extraction_service.extract(
                pdf_path,
                extraction_schema,
                user_prompt,
                extraction_config,
                layout_prompt,
            )
            logger.info("Content extracted successfully")

            # Update document with extracted content
            document.extracted_content = extracted_content
            document.update(self._context.datasource)

            # Transform content using translation schema
            transformed_content = transform_content(
                transformer, extracted_content, translation_schema
            )

            # Check if transformed content is empty
            if not transformed_content:
                raise DocumentServiceError(
                    "Transformation resulted in empty content. Please check the translation "
                    "rules and extracted content."
                )

            logger.info("Content transformed successfully")

            # Update document with transformed content
            document.translated_content = transformed_content
            document.update(self._context.datasource)

            # Populate comparison_v1_v2 table. TODO: Remove this once DIv1 is no longer supported.
            self._populate_v1_comparison_table(document)

            return document

        except Exception as e:
            logger.error(f"Error in document processing: {e!s}")
            raise DocumentServiceError(f"Document processing failed: {e!s}") from e

    def _execute_experiment(
        self,
        experiment: _Experiment,
        file_name: str,
        data_model: DataModel,
        layout_name: str,
        parsed_extraction_schema: dict[str, Any],
        parsed_translation_schema: dict[str, Any],
    ) -> _ExperimentResult:
        """Execute a single processing experiment.

        Args:
            experiment: The experiment configuration to execute
            file_name: Name of the file to process
            data_model: Data model for document
            layout_name: Document layout name
            parsed_extraction_schema: Parsed extraction schema
            parsed_translation_schema: Parsed translation schema

        Returns:
            ExperimentResult with success/failure information and error details
        """
        logger.info(f"Starting experiment: {experiment.name}")

        document = None
        try:
            # Process document with the experiment's configuration
            document = self._process_document_with_schemas(
                file_name=file_name,
                data_model=data_model,
                layout_name=layout_name,
                extraction_schema=parsed_extraction_schema,
                translation_schema=parsed_translation_schema,
                user_prompt=experiment.user_prompt,
                extraction_config=experiment.extraction_config,
                layout_prompt=experiment.layout_prompt,
            )

            validation_results = self._validate_and_store_schemas(
                data_model,
                document,
                parsed_extraction_schema,
                parsed_translation_schema,
                experiment.extraction_config,
            )

            logger.info(f"Experiment {experiment.name} succeeded")
            return _ExperimentResult(
                document=document,
                experiment_name=experiment.name,
                success=True,
                validation_results=validation_results,
            )

        except Exception as e:
            logger.info(f"Experiment {experiment.name} failed: {e}")
            return _ExperimentResult(
                document=document,
                experiment_name=experiment.name,
                success=False,
                error_message=f"{type(e).__name__}: {e!s}",
            )

    def _validate_and_store_schemas(
        self,
        data_model: DataModel,
        document: Document,
        parsed_extraction_schema: dict[str, Any],
        parsed_translation_schema: dict[str, Any],
        config_data: dict[str, Any] | None = None,
    ) -> ValidationSummary:
        """Validate document and store schemas on success.

        Args:
            document: Document to validate
            datasource: Data source connection
            parsed_extraction_schema: Parsed extraction schema
            parsed_translation_schema: Parsed translation schema
            config_data: Optional config data for retry scenarios

        Returns:
            Dict with validation results

        Raises:
            DocumentServiceError: If validation fails
        """
        # Attempt validation
        validation_response = self.validate(data_model, document.id)

        # Validation passed - store schemas
        DocumentLayout.upsert_schema(
            self._context.datasource,
            document.data_model,
            document.document_layout,
            parsed_extraction_schema,
            parsed_translation_schema,
            config_data,
        )

        return validation_response

    def _fetch_v1_data(self, document_name: str) -> dict[str, Any] | None:
        """Fetch v1 data from documents_v1 table.

        Args:
            document_name: Name of the document to fetch v1 data for

        Returns:
            The transformed_content JSON from documents_v1 table, or None if not found
        """
        try:
            sql = (
                "SELECT transformed_content FROM documents_v1 WHERE document_name = $document_name"
            )
            result = self._context.datasource.native_query(
                sql, params={"document_name": document_name}
            )

            rows = result.to_dict_list()
            if rows and len(rows) > 0:
                return rows[0]["transformed_content"]
            return None

        except Exception as e:
            logger.error(f"Failed to fetch v1 data for document {document_name}: {e!s}")
            return None

    def _populate_v1_comparison_table(self, document: Document) -> None:
        """Populate the comparison_v1_v2 table with data from both DI v1 and v2.

        Args:
            document: The document containing translated_content (v2)
        """
        try:
            if not document.translated_content:
                logger.warning(
                    f"Skipping comparison table population for document {document.id} - "
                    "missing v2 content"
                )
                return

            # Fetch v1 data from documents_v1 table
            v1_data = self._fetch_v1_data(document.document_name)
            if not v1_data:
                logger.warning(
                    f"Skipping comparison table population for document {document.id} - "
                    "no v1 data found"
                )
                return

            # Extract v1 data (from documents_v1.transformed_content)
            v1_invoice_total, v1_line_items_total, v1_line_items_count = (
                _extract_v1_totals_and_counts(v1_data)
            )

            # Extract v2 data (from translated_content)
            v2_invoice_total, v2_line_items_total, v2_line_items_count = (
                _extract_v2_totals_and_counts(document.translated_content)
            )

            # Insert or update comparison record
            sql = """
                INSERT INTO comparison_v1_v2 (
                    document_name, v1_invoice_total, v1_line_items_total, v1_line_items_count,
                    v2_invoice_total, v2_line_items_total, v2_line_items_count, updated_at
                ) VALUES (
                    $document_name, $v1_invoice_total, $v1_line_items_total, $v1_line_items_count,
                    $v2_invoice_total, $v2_line_items_total, $v2_line_items_count, NOW()
                )
                ON CONFLICT (document_name) DO UPDATE SET
                    v1_invoice_total = EXCLUDED.v1_invoice_total,
                    v1_line_items_total = EXCLUDED.v1_line_items_total,
                    v1_line_items_count = EXCLUDED.v1_line_items_count,
                    v2_invoice_total = EXCLUDED.v2_invoice_total,
                    v2_line_items_total = EXCLUDED.v2_line_items_total,
                    v2_line_items_count = EXCLUDED.v2_line_items_count,
                    updated_at = NOW()
            """

            self._context.datasource.native_query(
                sql,
                params={
                    "document_name": document.document_name,
                    "v1_invoice_total": v1_invoice_total,
                    "v1_line_items_total": v1_line_items_total,
                    "v1_line_items_count": v1_line_items_count,
                    "v2_invoice_total": v2_invoice_total,
                    "v2_line_items_total": v2_line_items_total,
                    "v2_line_items_count": v2_line_items_count,
                },
            )

            logger.info(
                f"Successfully populated comparison table for document {document.document_name}"
            )

        except Exception as e:
            logger.warning(
                f"Failed to populate comparison table for document "
                f"{document.document_name}: {e!s}. "
                "This is only for reporting v1 and can be ignored."
            )

    def _process_with_experiments(
        self,
        file_name: str,
        data_model: DataModel,
        layout_name: str,
        parsed_extraction_schema: dict[str, Any],
        parsed_translation_schema: dict[str, Any],
        data_model_prompt: str | None,
        extraction_config: dict[str, Any] | None,
        layout_prompt: str | None,
    ) -> _ProcessingResponse:
        """Process document by trying experiments until one succeeds.

        Args:
            file_name: Name of the file to process
            data_model: Data model for document
            layout_name: Document layout name
            parsed_extraction_schema: Parsed extraction schema
            parsed_translation_schema: Parsed translation schema
            data_model_prompt: Optional data model prompt for processing
            extraction_config: Optional Reducto extraction configuration
            layout_prompt: Optional layout prompt/system prompt

        Returns:
            ProcessingResponse with experiment results and final document

        Raises:
            DocumentServiceError: If all experiments fail
        """
        # Generate experiments to try
        experiments = self._generate_experiments(
            initial_extraction_config=extraction_config,
            initial_user_prompt=data_model_prompt,
            initial_layout_prompt=layout_prompt,
        )

        logger.info(f"Generated {len(experiments)} experiments to try")

        experiment_results = []
        for experiment in experiments:
            result: _ExperimentResult = self._execute_experiment(
                experiment=experiment,
                file_name=file_name,
                data_model=data_model,
                layout_name=layout_name,
                parsed_extraction_schema=parsed_extraction_schema,
                parsed_translation_schema=parsed_translation_schema,
            )

            experiment_results.append(result)

            if result.success:
                return _ProcessingResponse(
                    success=True,
                    document=result.document,
                    experiments=experiment_results,
                    successful_experiment=experiment.name,
                    total_attempts=len(experiment_results),
                )

        # All experiments failed
        failed_experiment_names = [r.experiment_name for r in experiment_results]
        error_message = (
            f"Document processing failed after {len(experiment_results)} experiments. "
            f"Tried experiments: {', '.join(failed_experiment_names)}. "
        )

        logger.error(error_message)
        raise DocumentServiceError(error_message)


def _parse_currency_string(value: str | float | int) -> float:
    """Parse currency string or number to float, handling common formats.

    Args:
        value: Currency string like "$3,263,400.00", "1234.56", or already a number

    Returns:
        Parsed float value or 0.0 if parsing fails
    """
    try:
        if value is None:
            return 0.0

        # If it's already a number, return it
        if isinstance(value, int | float):
            return float(value)

        if isinstance(value, str):
            # Remove currency symbols and whitespace
            cleaned = value.strip().replace("$", "").replace(",", "")

            # Check if value is enclosed in parentheses (negative)
            is_negative = cleaned.startswith("(") and cleaned.endswith(")")
            if is_negative:
                # Remove parentheses
                cleaned = cleaned[1:-1]
            result = float(cleaned)
            return -result if is_negative else result

        return 0.0
    except (ValueError, AttributeError):
        return 0.0


def _extract_v1_totals_and_counts(v1_json: dict[str, Any]) -> tuple[float, float, int]:
    """Extract totals and counts from v1 JSON format.

    Args:
        v1_json: The v1 JSON data (extracted_content)

    Returns:
        Tuple of (invoice_total, line_items_total, line_items_count)
    """
    try:
        # Extract invoice total from fields.Total
        invoice_total = 0
        if "fields" in v1_json and "Total" in v1_json["fields"]:
            invoice_total = float(v1_json["fields"]["Total"])

        # Extract line items total from additional_info.line_items_total
        line_items_total = 0
        if "additional_info" in v1_json and "line_items_total" in v1_json["additional_info"]:
            line_items_total = float(v1_json["additional_info"]["line_items_total"])

        # Count line items from table_data.line_items
        line_items_count = 0
        if "table_data" in v1_json and "line_items" in v1_json["table_data"]:
            line_items_count = len(v1_json["table_data"]["line_items"])

        return round(invoice_total, 2), round(line_items_total, 2), line_items_count
    except (KeyError, TypeError, ValueError):
        return 0.0, 0.0, 0


def _extract_v2_totals_and_counts(v2_json: dict[str, Any]) -> tuple[float, float, int]:
    """Extract totals and counts from v2 JSON format.

    Args:
        v2_json: The v2 JSON data (translated_content)

    Returns:
        Tuple of (invoice_total, line_items_total, line_items_count)
    """
    try:
        # Extract invoice total from Invoice_details.invoice_total
        invoice_total = 0.0
        line_items_total = 0.0
        line_items_count = 0
        if "Invoice_details" in v2_json and "invoice_total" in v2_json["Invoice_details"]:
            invoice_total = _parse_currency_string(v2_json["Invoice_details"]["invoice_total"])

        # Calculate line items total from Transactions array
        if "Transactions" in v2_json and isinstance(v2_json["Transactions"], list):
            transactions = v2_json["Transactions"]
            line_items_count = len(transactions)

            # Sum up all transaction amounts (can be negative)
            total_amount = 0.0
            for transaction in transactions:
                if "amount" in transaction:
                    amount = _parse_currency_string(transaction["amount"])
                    total_amount += amount
            line_items_total = total_amount

        return round(invoice_total, 2), round(line_items_total, 2), line_items_count
    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Failed to extract totals and counts from v2 JSON: {e!s}")
        return 0.0, 0.0, 0


def _configs_are_equivalent(config1: dict[str, Any], config2: dict[str, Any]) -> bool:
    """Compare two extraction configs to determine if they are functionally equivalent.

    Args:
        config1: First config to compare
        config2: Second config to compare

    Returns:
        True if configs are equivalent, False otherwise
    """
    # Handle None cases
    if config1 is None and config2 is None:
        return True
    if config1 is None or config2 is None:
        return False

    # Deep comparison of config dictionaries
    try:
        return config1 == config2
    except Exception:
        # Fallback to string comparison if direct comparison fails
        return str(config1) == str(config2)
