import json
import uuid
from unittest.mock import patch

import pytest

from sema4ai_docint.extraction.process import ExtractAndTransformContentParams
from sema4ai_docint.models.data_model import DataModel
from sema4ai_docint.models.document import Document
from sema4ai_docint.models.document_layout import DocumentLayout
from sema4ai_docint.services.exceptions import DocumentServiceError


class TestDocumentService:
    @pytest.fixture
    def setup_test_data(self, postgres_datasource, data_model_data, document_layout_data):
        """Set up test data by actually inserting into the PostgreSQL database."""
        data_model = DataModel(
            name=data_model_data["name"],
            description=data_model_data["description"],
            model_schema=data_model_data["model_schema"],
            views=data_model_data["views"],
            quality_checks=data_model_data["quality_checks"],
            prompt=data_model_data["prompt"],
            summary=data_model_data["summary"],
        )

        document_layout = DocumentLayout(
            name=document_layout_data["name"],
            data_model=document_layout_data["data_model"],
            extraction_schema=json.loads(document_layout_data["extraction_schema"]),
            translation_schema=json.loads(document_layout_data["translation_schema"]),
            summary=document_layout_data["summary"],
            system_prompt=document_layout_data.get("system_prompt"),
        )

        data_model.insert(postgres_datasource)
        document_layout.insert(postgres_datasource)

        test_data = {"data_model": data_model, "document_layout": document_layout}

        return test_data

    @pytest.fixture
    def setup_test_document(self, setup_test_data, document_data, postgres_datasource):
        """Set up a test document by actually inserting into the PostgreSQL database."""
        document = Document(
            id=document_data["id"],
            document_name=document_data["document_name"],
            document_layout=document_data["document_layout"],
            data_model=document_data["data_model"],
            extracted_content=json.loads(document_data["extracted_content"]),
            translated_content=json.loads(document_data["translated_content"]),
        )

        document.insert(postgres_datasource)

        test_data = {"document": document, **setup_test_data}

        return test_data

    def test_query_success(
        self,
        setup_db,
        document_service,
        setup_test_document,
        cleanup_db,
    ):
        """Test successful document query using data repo pattern."""
        test_data = setup_test_document
        document = test_data["document"]

        result = document_service.query(document.id)

        assert result is not None
        assert "TEST_ITEMS" in result

    def test_query_document_not_found(self, document_service):
        non_existent_id = str(uuid.uuid4())

        with pytest.raises(DocumentServiceError, match="Document with ID .* not found"):
            document_service.query(non_existent_id)

    def test_query_data_model_not_found(
        self,
        setup_db,
        document_service,
        postgres_datasource,
        setup_test_data,
        cleanup_db,
    ):
        """Test query when document exists but data model doesn't."""
        # Create a document with non-existent data model
        document = Document(
            id=str(uuid.uuid4()),
            document_name="test.pdf",
            document_layout=setup_test_data["document_layout"].name,
            data_model="non_existent_model",
            extracted_content={},
            translated_content={},
        )
        document.insert(postgres_datasource)

        with pytest.raises(DocumentServiceError, match="Data model with name .* not found"):
            document_service.query(document.id)

    def test_ingest_success(
        self,
        setup_db,
        document_service,
        setup_test_data,
        test_pdf_path,
        cleanup_db,
    ):
        data_model = setup_test_data["data_model"]
        document_layout = setup_test_data["document_layout"]

        with patch("sema4ai_docint.services._document.get_file", return_value=test_pdf_path):
            with patch(
                "sema4ai_docint.extraction.transform.transform_document_layout.TransformDocumentLayout.get_doc_uuid",
                return_value=str(uuid.uuid4()),
            ):
                result = document_service.ingest(
                    file_name="INV-00001.pdf",
                    data_model_name=data_model.name,
                    layout_name=document_layout.name,
                )

                assert result is not None
                assert "document" in result

    def test_ingest_data_model_not_found(self, document_service):
        """Test ingestion when data model doesn't exist."""
        with pytest.raises(DocumentServiceError, match="Data model .* not found"):
            document_service.ingest(
                file_name="test.pdf",
                data_model_name="non_existent_model",
                layout_name="test_layout",
            )

    def test_ingest_layout_not_found(self, setup_db, document_service, setup_test_data, cleanup_db):
        """Test ingestion when document layout doesn't exist."""
        data_model = setup_test_data["data_model"]

        with pytest.raises(DocumentServiceError, match="Document layout does not exist"):
            document_service.ingest(
                file_name="test.pdf",
                data_model_name=data_model.name,
                layout_name="non_existent_layout",
            )

    def test_extract_with_schema_success(
        self, setup_db, document_service, setup_test_data, test_pdf_path, cleanup_db
    ):
        """Test successful content extraction with provided schemas."""
        data_model = setup_test_data["data_model"]
        document_layout = setup_test_data["document_layout"]

        params = ExtractAndTransformContentParams(
            file_name="INV-00001.pdf",
            extraction_schema=json.dumps(document_layout.extraction_schema),
            translation_schema=document_layout.translation_schema,
            data_model_name=data_model.name,
            layout_name="test_layout",
        )

        with patch("sema4ai_docint.services._document.get_file", return_value=test_pdf_path):
            with patch(
                "sema4ai_docint.extraction.transform.transform_document_layout.TransformDocumentLayout.get_doc_uuid",
                return_value=str(uuid.uuid4()),
            ):
                result = document_service.extract_with_schema(params)

                assert result is not None
                assert "document" in result
                assert "success" in result
                assert "experiments" in result
                assert "successful_experiment" in result
                assert result["success"] is True
                assert result["successful_experiment"] == "default"

                # Verify document was created with custom schema
                document_dict = result["document"]
                assert document_dict["document_name"] == "INV-00001.pdf"
                assert document_dict["data_model"] == data_model.name

                # Verify experiments structure
                experiments = result["experiments"]
                assert len(experiments) > 0
                successful_experiment = next(
                    (exp for exp in experiments if exp["success"] is True), None
                )
                assert successful_experiment is not None
                assert "validation_results" in successful_experiment

    def test_extract_with_schema_data_model_not_found(self, document_service):
        """Test extraction when data model doesn't exist."""
        params = ExtractAndTransformContentParams(
            file_name="test.pdf",
            extraction_schema='{"type": "object"}',
            translation_schema={"rules": [{"source": "test", "target": "test"}]},
            data_model_name="non_existent_model",
            layout_name="test_layout",
        )

        with pytest.raises(DocumentServiceError, match="Data model .* not found"):
            document_service.extract_with_schema(params)

    def test_validate_success(
        self,
        setup_db,
        document_service,
        setup_test_document,
        cleanup_db,
        drop_mindsdb_views,
    ):
        """Test successful document validation with real quality checks."""
        test_data = setup_test_document
        document = test_data["document"]
        data_model = test_data["data_model"]

        result = document_service.validate(
            data_model=data_model,
            document_id=document.id,
        )

        assert result is not None
        assert result.overall_status == "passed"
        assert result.passed == 1
        assert result.failed == 0
        assert result.errors == 0
        assert len(result.results) == 1
        assert result.results[0].rule_name == "validate_total_with_item_sum"
        assert result.results[0].status == "passed"

    def test_validate_failed_validation(
        self,
        setup_db,
        document_service,
        postgres_datasource,
        setup_test_data,
        cleanup_db,
    ):
        """Test validation when document fails quality checks."""
        datasource = postgres_datasource
        data_model = setup_test_data["data_model"]

        bad_translated_content = {
            "items": [
                {
                    "rate": "$100.00",
                    "amount": "$100.00",
                    "quantity": "1",
                    "description": "Item 1",
                },
                {
                    "rate": "$200.00",
                    "amount": "$200.00",
                    "quantity": "1",
                    "description": "Item 2",
                },
            ],
            "total": "$500.00",
            "invoice_number": "INV-BAD",
            "date_issued": "2025-01-01",
            "due_date": "2025-02-01",
            "billed_to": "Test Client",
            "amount_due": "$500.00",
            "balance_due": "$500.00",
        }

        bad_document = Document(
            id=str(uuid.uuid4()),
            document_name="bad_invoice.pdf",
            document_layout=setup_test_data["document_layout"].name,
            data_model=data_model.name,
            extracted_content=bad_translated_content,
            translated_content=bad_translated_content,
        )
        bad_document.insert(datasource)

        with pytest.raises(DocumentServiceError, match="Document validation encountered errors"):
            document_service.validate(
                data_model=data_model,
                document_id=bad_document.id,
            )

    def test_data_quality_checks_not_required(self, document_service):
        data_model = DataModel(
            name="test_data_model",
            description="Test data model",
            model_schema={},
            views=[],
            quality_checks=[],
        )

        validation_summary = document_service.validate(
            data_model=data_model, document_id="test_document_id"
        )
        assert validation_summary.overall_status == "passed"
        assert len(validation_summary.results) == 0
        assert validation_summary.passed == 0
        assert validation_summary.failed == 0
        assert validation_summary.errors == 0

    def test_reducto_config_succeeds_when_default_fails(
        self, setup_db, document_service, setup_test_data, test_pdf_path, cleanup_db
    ):
        """Test scenario where default (layout) config fails but Reducto config succeeds."""
        data_model = setup_test_data["data_model"]
        document_layout = setup_test_data["document_layout"]

        params = ExtractAndTransformContentParams(
            file_name="INV-00001.pdf",
            extraction_schema=json.dumps(document_layout.extraction_schema),
            translation_schema=document_layout.translation_schema,
            data_model_name=data_model.name,
            layout_name="test_layout",
        )

        # Track call count to make first extraction fail, second succeed
        call_count = 0
        original_extract = document_service._context.extraction_service.extract

        def mock_extract_with_retry(file_path, schema, user_prompt, config, layout_prompt):
            nonlocal call_count
            call_count += 1

            # First call (default config) - simulate failure
            if call_count == 1:
                raise Exception("Default extraction configuration failed")

            # Second call (Reducto config) - simulate success
            elif call_count == 2:
                # Return successful extraction content
                return {
                    "invoice_number": "INV-00001",
                    "date_issued": "2025-01-01",
                    "due_date": "2025-02-01",
                    "billed_to": "Test Client",
                    "total": "$300.00",
                    "amount_due": "$300.00",
                    "balance_due": "$300.00",
                    "items": [
                        {
                            "description": "Item 1",
                            "quantity": "1",
                            "rate": "$100.00",
                            "amount": "$100.00",
                        },
                        {
                            "description": "Item 2",
                            "quantity": "1",
                            "rate": "$200.00",
                            "amount": "$200.00",
                        },
                    ],
                }
            else:
                # Shouldn't reach here in this test
                return original_extract(file_path, schema, user_prompt, config, layout_prompt)

        with patch("sema4ai_docint.services._document.get_file", return_value=test_pdf_path):
            with patch(
                "sema4ai_docint.extraction.transform.transform_document_layout.TransformDocumentLayout.get_doc_uuid",
                return_value=str(uuid.uuid4()),
            ):
                # Mock the extraction service to fail first, succeed second
                document_service._context.extraction_service.extract = mock_extract_with_retry

                try:
                    result = document_service.extract_with_schema(params)

                    # Verify the overall result
                    assert result is not None
                    assert "document" in result
                    assert "success" in result
                    assert "experiments" in result
                    assert "successful_experiment" in result
                    assert result["success"] is True

                    # Verify we tried multiple experiments
                    experiments = result["experiments"]
                    assert len(experiments) >= 2

                    # First experiment (default) should have failed
                    first_experiment = experiments[0]
                    assert first_experiment["experiment_name"] == "default"
                    assert first_experiment["success"] is False
                    assert "error_message" in first_experiment
                    assert (
                        "Default extraction configuration failed"
                        in first_experiment["error_message"]
                    )

                    # Second experiment (Reducto config) should have succeeded
                    second_experiment = experiments[1]
                    assert second_experiment["experiment_name"].startswith("reducto_")
                    assert second_experiment["success"] is True
                    assert "validation_results" in second_experiment

                    # Verify the successful experiment name matches the second experiment
                    assert result["successful_experiment"] == second_experiment["experiment_name"]
                    assert result["successful_experiment"].startswith("reducto_")

                    # Verify validation results are present and successful
                    validation_results = second_experiment["validation_results"]
                    assert validation_results["overall_status"] == "passed"

                    # Verify total attempts
                    assert result["total_attempts"] == 2

                finally:
                    # Restore original method
                    document_service._context.extraction_service.extract = original_extract
