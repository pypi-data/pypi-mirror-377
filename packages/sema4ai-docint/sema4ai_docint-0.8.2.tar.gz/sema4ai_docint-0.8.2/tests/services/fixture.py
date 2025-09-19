import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from sema4ai_docint.models.data_model import DataModel
from sema4ai_docint.services._context import _DIContext
from sema4ai_docint.services._data_model import _DataModelService
from sema4ai_docint.services._document import _DocumentService
from sema4ai_docint.services._extraction import _ExtractionService
from sema4ai_docint.services._knowledge_base_service import _KnowledgeBaseService
from sema4ai_docint.services._layout import _LayoutService
from tests.agent_dummy_server import AgentDummyServer


@pytest.fixture
def data_model_data(mindsdb_db_name: str) -> dict[str, Any]:
    """Load test data model from JSON file and substitute the correct database name."""
    with open(Path(__file__).parent / "assets" / "data_model.json") as f:
        data = json.load(f)

    data_model = data[0]
    if data_model.get("views"):
        for view in data_model["views"]:
            if "sql" in view:
                import re

                view["sql"] = re.sub(r"`test_postgres_\d+`", f"`{mindsdb_db_name}`", view["sql"])

    return data_model


@pytest.fixture
def document_layout_data() -> dict[str, Any]:
    """Load test document layout from JSON file."""
    with open(Path(__file__).parent / "assets" / "document_layout.json") as f:
        data = json.load(f)
    return data[0]


@pytest.fixture
def document_data() -> dict[str, Any]:
    """Load test document from JSON file."""
    with open(Path(__file__).parent / "assets" / "document.json") as f:
        data = json.load(f)
    return data[0]


@pytest.fixture
def test_pdf_path() -> str:
    """Return path to test PDF file for service tests."""
    return str(Path(__file__).parent / "assets" / "INV-00001.pdf")


@pytest.fixture
def extraction_service(agent_dummy_server):
    """Create an extraction service with test API key and mock its methods."""
    service = _ExtractionService(sema4_api_key="test_api_key")
    service.extract = Mock(
        return_value={
            "items": [
                {
                    "rate": "$55.00",
                    "amount": "$5,500.00",
                    "quantity": "100",
                    "description": "Services",
                },
                {
                    "rate": "$35.00",
                    "amount": "$1,750.00",
                    "quantity": "50",
                    "description": "Support",
                },
            ],
            "total": "$7,250.00",
            "due_date": "September 19, 2025",
            "billed_to": "Test Client",
            "amount_due": "$7,250.00",
            "balance_due": "$7,250.00",
            "date_issued": "August 20, 2025",
            "invoice_number": "INV-TEST-001",
        }
    )
    return service


@pytest.fixture
def context(postgres_datasource, extraction_service):
    """Create a context with actual datasource and extraction service."""
    return _DIContext(datasource=postgres_datasource, extraction_service=extraction_service)


@pytest.fixture
def document_service(context):
    """Create a DocumentService instance for testing."""
    return _DocumentService(context)


@pytest.fixture
def layout_service(context):
    """Create a LayoutService instance for testing."""
    return _LayoutService(context)


@pytest.fixture
def data_model_service(context):
    """Create a DataModelService instance for testing."""
    return _DataModelService(context)


@pytest.fixture
def knowledge_base_service(context):
    """Create a KnowledgeBaseService instance for testing."""
    return _KnowledgeBaseService(context)


@pytest.fixture
def drop_mindsdb_views():
    """Ensure MindsDB views are dropped before and after each test to avoid stale integrations."""
    from sema4ai.data import get_connection

    from sema4ai_docint.models.constants import PROJECT_NAME

    yield

    conn = get_connection()
    conn.execute_sql(f"DROP VIEW IF EXISTS {PROJECT_NAME}.TEST_ITEMS")


@pytest.fixture
def setup_data_model(postgres_datasource, data_model_data):
    """Set up a test data model by inserting into the PostgreSQL database."""
    data_model = DataModel(**data_model_data)
    data_model.insert(postgres_datasource)
    return data_model


@pytest.fixture
def agent_dummy_server(request):
    """Start AgentDummyServer for testing with configurable responses."""
    from pathlib import Path

    # Get responses from test parameter if provided
    responses = getattr(request, "param", None)

    # Start the dummy server
    server = AgentDummyServer(responses)
    server.start()

    # Set environment variables to point to the dummy server
    original_agents_url = os.environ.get("SEMA4AI_AGENTS_SERVICE_URL")
    original_file_url = os.environ.get("SEMA4AI_FILE_MANAGEMENT_URL")

    os.environ["SEMA4AI_AGENTS_SERVICE_URL"] = f"http://localhost:{server.get_port()}"

    # Set up file management URL for test data
    test_data_dir = Path(__file__).parent / "assets"
    os.environ["SEMA4AI_FILE_MANAGEMENT_URL"] = f"file://{test_data_dir.absolute()}"

    try:
        yield server
    finally:
        # Cleanup
        server.stop()

        # Restore original environment variables
        if original_agents_url is not None:
            os.environ["SEMA4AI_AGENTS_SERVICE_URL"] = original_agents_url
        else:
            os.environ.pop("SEMA4AI_AGENTS_SERVICE_URL", None)

        if original_file_url is not None:
            os.environ["SEMA4AI_FILE_MANAGEMENT_URL"] = original_file_url
        else:
            os.environ.pop("SEMA4AI_FILE_MANAGEMENT_URL", None)
