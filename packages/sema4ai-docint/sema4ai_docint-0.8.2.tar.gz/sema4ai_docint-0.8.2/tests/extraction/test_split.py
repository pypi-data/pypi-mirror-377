import json
from pathlib import Path
from typing import Any

import pytest
from reducto.types import SplitCategory

from sema4ai_docint.extraction import ExtractionClient
from sema4ai_docint.logging import _setup_logging, logger

_setup_logging()


@pytest.mark.reducto_eval
class TestDocumentSplit:
    def test_split_farris(self, client: ExtractionClient, request):
        base = Path(__file__).parent / "test-data" / "split" / "farris"
        file_name = base / "data.pdf"
        expected_file = base / "expected_splits.json"

        # Read the expected split response
        with open(expected_file) as f:
            expected = json.load(f)

        # Upload
        uploaded_file_url = client.upload(file_name)

        # Parse
        parse_response = client.parse(uploaded_file_url)

        assert parse_response
        assert parse_response.job_id

        job_id = f"jobid://{parse_response.job_id}"

        resp = client.split(
            job_id,
            [
                SplitCategory(
                    name="Capacity Tables",
                    description="Pages with tables which relate to the limits of components",
                ),
            ],
        )
        assert resp

        expected_capacity_tables = expected["result"]["section_mapping"]["Capacity Tables"]
        actual_capacity_tables = resp.model_dump()["result"]["section_mapping"]["Capacity Tables"]

        # Calculate overlap percentage between expected and actual capacity tables
        common_pages = set(expected_capacity_tables) & set(actual_capacity_tables)
        overlap_percentage = (
            len(common_pages)
            / max(len(expected_capacity_tables), len(actual_capacity_tables))
            * 100
        )

        logger.info(f"Expected pages with capacity tables: {expected_capacity_tables}")
        logger.info(f"Actual pages with capacity tables: {actual_capacity_tables}")

        assert overlap_percentage >= 80, (
            f"Capacity Tables sections only overlap by {overlap_percentage:.1f}% (expected >= 80%)"
        )

    def test_extract_with_splits(self, client: ExtractionClient, request):
        base = Path(__file__).parent / "test-data" / "split" / "farris"
        file_name = base / "data.pdf"
        schema_file = base / "schema.json"

        assert file_name.exists()
        assert schema_file.exists()

        with open(schema_file) as f:
            schema = json.load(f)

        # Upload
        uploaded_file_url = client.upload(file_name)

        # Parse
        parse_response = client.parse(uploaded_file_url)

        assert parse_response
        assert parse_response.job_id

        job_id = f"jobid://{parse_response.job_id}"

        resp = client.split(
            job_id,
            [
                SplitCategory(
                    name="Capacity Tables",
                    description="Pages with tables which relate to the limits of components",
                ),
            ],
        )
        assert resp

        # limit the pages we consider
        capacity_table_pages = resp.result.section_mapping["Capacity Tables"]
        page = 39  # a known page with a capacity table
        assert page in capacity_table_pages

        # Limit the extraction to only relevant pages
        extract_response = client.extract(uploaded_file_url, schema, start_page=page, end_page=page)

        # Verify the extraction
        assert extract_response
        assert extract_response.result

        results = extract_response.result
        assert len(results) == 1
        actual: dict[str, Any] = results[0]  # type: ignore

        logger.info(f"Extract result: {json.dumps(actual, indent=2)}")

        assert "capacityTables" in actual
        actual_tables = actual["capacityTables"]
        assert len(actual_tables) == 1
        actual_table = actual_tables[0]

        assert "US" == actual_table["units"]
        assert "ASME" == actual_table["code"]
        assert 10 == actual_table["overpressurePercent"]
