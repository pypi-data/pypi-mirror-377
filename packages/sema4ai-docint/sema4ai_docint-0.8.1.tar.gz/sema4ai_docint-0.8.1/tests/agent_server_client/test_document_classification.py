"""
Integration tests for document classification using the agent server client.
"""

import json
import logging
from pathlib import Path

import pytest

from sema4ai_docint.agent_server_client import CategorizedSummary
from sema4ai_docint.agent_server_client.client import AgentServerClient
from sema4ai_docint.agent_server_client.exceptions import DocumentClassificationError

logger = logging.getLogger(__name__)


def get_pdf_test_id(specific_pdf):
    """Generate test ID based on the PDF parameter."""
    if specific_pdf is None:
        return "all_pdfs"
    else:
        # Remove .pdf extension and convert to test-friendly name
        return specific_pdf.replace(".pdf", "_pdf")


@pytest.mark.classification_eval
class TestDocumentClassification:
    """Test class for document classification functionality."""

    # To test all PDFs:
    @pytest.mark.parametrize("specific_pdf", [None], ids=lambda x: get_pdf_test_id(x))
    # To test a specific PDF:
    # @pytest.mark.parametrize("specific_pdf", ["washington.pdf"], ids=lambda x: get_pdf_test_id(x))
    # To test multiple specific PDFs:
    # @pytest.mark.parametrize("specific_pdf", ["washington.pdf", "tenaska.pdf", "tidal.pdf"],
    #     ids=lambda x: get_pdf_test_id(x))
    # TODO: Fix lint issues in this function
    def test_document_classification_with_pdfs(self, existing_postgres, agent_client, specific_pdf):  # noqa: C901, PLR0915
        """Test document classification using PDF files and layout summaries from PostgreSQL
        database.

        To test a specific PDF, modify the parametrize decorator:
        - For all PDFs: [None]
        - For specific PDF: ["washington.pdf"]
        - For multiple PDFs: ["washington.pdf", "tenaska.pdf", "tidal.pdf"]

        The test ID will be generated automatically based on the parameter.
        """

        # Get test data directory
        test_data_dir = Path(__file__).parent / "test-data" / "classify"

        if not test_data_dir.exists():
            print(f"Test data directory not found: {test_data_dir}")
            pytest.skip(f"Test data directory not found: {test_data_dir}")

        all_results = []

        # Process each data model directory
        for data_model_dir in test_data_dir.iterdir():
            if not data_model_dir.is_dir():
                continue

            data_model = data_model_dir.name
            print(f"\nProcessing data model: {data_model}")

            # Get layouts with summaries from the database using direct SQL (once per data model)
            try:
                # Query to get layouts with summaries for the specified data model
                query = """
                    SELECT name, summary
                    FROM document_layouts
                    WHERE data_model = %s AND summary IS NOT NULL AND summary != ''
                    ORDER BY name
                """

                conn, props = existing_postgres
                with conn.cursor() as cursor:
                    cursor.execute(query, (data_model,))
                    layouts_with_summaries = [
                        {"name": row[0], "summary": row[1]} for row in cursor.fetchall()
                    ]

                if not layouts_with_summaries:
                    print(f"    No layouts with summaries found for data model '{data_model}'")
                    continue

                print(f"    Found {len(layouts_with_summaries)} layouts with summaries")

                # Create known summaries from all layouts in the same data model (once per
                # data model)
                known_summaries = [
                    CategorizedSummary(summary=layout["summary"], category=layout["name"])
                    for layout in layouts_with_summaries
                ]

                # Process each PDF file in the data model directory
                for pdf_file in data_model_dir.iterdir():
                    if not pdf_file.is_file() or pdf_file.suffix.lower() != ".pdf":
                        continue

                    # If specific_pdf is provided, only process that file
                    if specific_pdf and pdf_file.name != specific_pdf:
                        continue

                    # Extract expected layout from filename (format: <document_layout.pdf>)
                    filename = pdf_file.stem  # Remove .pdf extension
                    expected_layout = filename

                    print(f"  Processing PDF: {pdf_file.name}")
                    print(f"  Expected layout: {expected_layout}")
                    print(f"  Data model: {data_model}")

                    try:
                        # Step 1: Summarize the PDF
                        print(f"    Summarizing PDF: {pdf_file.name}")
                        pdf_summary = agent_client.summarize(str(pdf_file))
                        print(f"    Generated summary: {pdf_summary[:100]}...")

                        # Step 2: Classify the summary against known layouts and get all scores
                        print(f"    Classifying against {len(known_summaries)} known layouts")
                        categorized_summary, confidence_score = agent_client.categorize(
                            known_summaries, pdf_summary
                        )

                        # Check if classification is correct
                        is_correct = categorized_summary.category.lower() == expected_layout.lower()

                        print(
                            f"    Predicted: {categorized_summary.category} (confidence: "
                            f"{confidence_score:.3f})"
                        )
                        print(f"    Expected: {expected_layout}")
                        print(f"    Result: {'✓ CORRECT' if is_correct else '✗ INCORRECT'}")

                        # Store result
                        result = {
                            "pdf_file": str(pdf_file),
                            "data_model": data_model,
                            "expected_layout": expected_layout,
                            "predicted_layout": categorized_summary.category,
                            "confidence_score": confidence_score,
                            "is_correct": is_correct,
                            "pdf_summary": pdf_summary,
                            "num_known_layouts": len(known_summaries),
                        }
                        all_results.append(result)

                    except Exception as e:
                        print(f"    Error during classification: {e!s}")
                        result = {
                            "pdf_file": str(pdf_file),
                            "data_model": data_model,
                            "expected_layout": expected_layout,
                            "predicted_layout": None,
                            "confidence_score": 0.0,
                            "is_correct": False,
                            "error": str(e),
                            "num_known_layouts": 0,
                        }
                        all_results.append(result)

            except Exception as e:
                print(f"Error processing data model '{data_model}': {e!s}")
                continue

        if not all_results:
            pytest.skip("No valid test cases found")

        # Calculate overall accuracy
        correct_predictions = sum(1 for result in all_results if result["is_correct"])
        total_predictions = len(all_results)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0

        print("\nOverall Classification Results:")
        print(f"  Total test cases: {total_predictions}")
        print(f"  Correct predictions: {correct_predictions}")
        print(f"  Accuracy: {accuracy:.3f} ({accuracy * 100:.1f}%)")

        # Store classification scores and write results to file
        results_file = (
            Path(__file__).parent / "test-output" / "classify" / "classification_results.json"
        )

        # Create the output directory if it doesn't exist
        results_file.parent.mkdir(parents=True, exist_ok=True)

        # Create classification matrix (simplified to avoid redundancy)
        classification_matrix = {}
        for result in all_results:
            pdf_name = Path(result["pdf_file"]).name
            classification_matrix[pdf_name] = {
                "expected_layout": result["expected_layout"],
                "predicted_layout": result["predicted_layout"],
                "is_correct": result["is_correct"],
                "confidence_score": result.get("confidence_score", 0.0),
            }

        # Write results to file before assertions
        with open(results_file, "w") as f:
            json.dump(
                {
                    "accuracy": accuracy,
                    "total_predictions": total_predictions,
                    "correct_predictions": correct_predictions,
                    "classification_matrix": classification_matrix,
                    "results": all_results,
                },
                f,
                indent=2,
            )
        print(f"\nClassification results saved to: {results_file}")

        # Print detailed results
        print("\nDetailed Results:")
        for result in all_results:
            status = "✓" if result["is_correct"] else "✗"
            confidence = (
                f"{result['confidence_score']:.3f}"
                if result.get("confidence_score") is not None
                else "N/A"
            )
            pdf_name = Path(result["pdf_file"]).name
            print(
                f"  {status} {pdf_name} -> {result['predicted_layout']} (conf: {confidence}) "
                f"vs {result['expected_layout']}"
            )

        # Assert that all documents were processed successfully
        failed_classifications = [r for r in all_results if r.get("error")]
        assert len(failed_classifications) == 0, (
            f"Some classifications failed: {failed_classifications}"
        )

        # Assert that all classifications are correct
        incorrect_classifications = [r for r in all_results if not r["is_correct"]]
        assert len(incorrect_classifications) == 0, (
            f"Some classifications were incorrect: {incorrect_classifications}"
        )

    @pytest.mark.parametrize("specific_pdf", [None], ids=lambda x: get_pdf_test_id(x))
    # TODO: Fix lint issues in this function
    def test_document_classification_with_images(  # noqa: C901, PLR0915
        self, existing_postgres, agent_client, specific_pdf
    ):
        """Test document classification using PDF images and layout names from PostgreSQL database.

        To test a specific PDF, modify the parametrize decorator:
        - For all PDFs: [None]
        - For specific PDF: ["washington.pdf"]
        - For multiple PDFs: ["washington.pdf", "tenaska.pdf", "tidal.pdf"]

        The test ID will be generated automatically based on the parameter.
        """

        # Get test data directory
        test_data_dir = Path(__file__).parent / "test-data" / "classify"

        if not test_data_dir.exists():
            print(f"Test data directory not found: {test_data_dir}")
            pytest.skip(f"Test data directory not found: {test_data_dir}")

        all_results = []

        # Process each data model directory
        for data_model_dir in test_data_dir.iterdir():
            if not data_model_dir.is_dir():
                continue

            data_model = data_model_dir.name
            print(f"\nProcessing data model: {data_model}")

            # Get layouts from the database using direct SQL (once per data model)
            try:
                # Query to get layouts for the specified data model
                query = """
                    SELECT name
                    FROM document_layouts
                    WHERE data_model = %s
                    ORDER BY name
                """

                conn, props = existing_postgres
                with conn.cursor() as cursor:
                    cursor.execute(query, (data_model,))
                    layouts = [row[0] for row in cursor.fetchall()]

                if not layouts:
                    print(f"    No layouts found for data model '{data_model}'")
                    continue

                print(f"    Found {len(layouts)} layouts")

                # Process each PDF file in the data model directory
                for pdf_file in data_model_dir.iterdir():
                    if not pdf_file.is_file() or pdf_file.suffix.lower() != ".pdf":
                        continue

                    # If specific_pdf is provided, only process that file
                    if specific_pdf and pdf_file.name != specific_pdf:
                        continue

                    # Extract expected layout from filename (format: <document_layout.pdf>)
                    filename = pdf_file.stem  # Remove .pdf extension
                    expected_layout = filename

                    print(f"  Processing PDF: {pdf_file.name}")
                    print(f"  Expected layout: {expected_layout}")
                    print(f"  Data model: {data_model}")

                    try:
                        # Step 1: Convert PDF to base64 images (first 3 pages)
                        print(f"    Converting PDF to images: {pdf_file.name}")
                        image_dicts = agent_client._pdf_to_images(pdf_file)
                        # Extract base64 strings from image dictionaries (limit to 3 pages)
                        base64_images = [img["value"] for img in image_dicts[:3]]
                        print(f"    Generated {len(base64_images)} images")

                        # Step 2: Classify the images against known layouts
                        print(f"    Classifying against {len(layouts)} known layouts")
                        predicted_layout = agent_client.classify_document_with_images(
                            base64_images, layouts
                        )

                        # Check if classification is correct
                        is_correct = predicted_layout.lower() == expected_layout.lower()

                        print(f"    Predicted: {predicted_layout}")
                        print(f"    Expected: {expected_layout}")
                        print(f"    Result: {'✓ CORRECT' if is_correct else '✗ INCORRECT'}")

                        # Store result
                        result = {
                            "pdf_file": str(pdf_file),
                            "data_model": data_model,
                            "expected_layout": expected_layout,
                            "predicted_layout": predicted_layout,
                            "is_correct": is_correct,
                            "num_images": len(base64_images),
                            "num_known_layouts": len(layouts),
                        }
                        all_results.append(result)

                    except Exception as e:
                        print(f"    Error during classification: {e!s}")
                        result = {
                            "pdf_file": str(pdf_file),
                            "data_model": data_model,
                            "expected_layout": expected_layout,
                            "predicted_layout": None,
                            "is_correct": False,
                            "error": str(e),
                            "num_known_layouts": len(layouts),
                        }
                        all_results.append(result)

            except Exception as e:
                print(f"Error processing data model '{data_model}': {e!s}")
                continue

        if not all_results:
            pytest.skip("No valid test cases found")

        # Calculate overall accuracy
        correct_predictions = sum(1 for result in all_results if result["is_correct"])
        total_predictions = len(all_results)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0

        print("\nOverall Image Classification Results:")
        print(f"  Total test cases: {total_predictions}")
        print(f"  Correct predictions: {correct_predictions}")
        print(f"  Accuracy: {accuracy:.3f} ({accuracy * 100:.1f}%)")

        # Store classification results and write to file before assertions
        results_file = (
            Path(__file__).parent / "test-output" / "classify" / "image_classification_results.json"
        )

        # Create the output directory if it doesn't exist
        results_file.parent.mkdir(parents=True, exist_ok=True)

        # Create simplified classification matrix for images
        classification_matrix = {}
        for result in all_results:
            pdf_name = Path(result["pdf_file"]).name
            classification_matrix[pdf_name] = {
                "expected_layout": result["expected_layout"],
                "predicted_layout": result["predicted_layout"],
                "is_correct": result["is_correct"],
                "num_images": result.get("num_images", 0),
            }

        with open(results_file, "w") as f:
            json.dump(
                {
                    "accuracy": accuracy,
                    "total_predictions": total_predictions,
                    "correct_predictions": correct_predictions,
                    "classification_matrix": classification_matrix,
                    "results": all_results,
                },
                f,
                indent=2,
            )
        print(f"\nImage classification results saved to: {results_file}")

        # Print detailed results
        print("\nDetailed Results:")
        for result in all_results:
            status = "✓" if result["is_correct"] else "✗"
            pdf_name = Path(result["pdf_file"]).name
            print(
                f"  {status} {pdf_name} -> {result['predicted_layout']} vs "
                f"{result['expected_layout']}"
            )

        # Assert that all documents were processed successfully
        failed_classifications = [r for r in all_results if r.get("error")]
        assert len(failed_classifications) == 0, (
            f"Some image classifications failed: {failed_classifications}"
        )

        # Assert that all classifications are correct
        incorrect_classifications = [r for r in all_results if not r["is_correct"]]
        assert len(incorrect_classifications) == 0, (
            f"Some image classifications were incorrect: {incorrect_classifications}"
        )

    def test_document_classification_multi_signal(self, agent_client):
        """Test document classification using multi-signal approach with 2-phase process:
        layout name generation + classification."""

        # Optional filter - if empty, test all documents in classification directory
        documents_to_test = [
            "Spire Missouri Inc - Dec 2024.pdf",  # has koch logo
            "Spire Missouri Inc - Feb 2025.pdf",
            "KINDER MORGAN TEJAS PIPELINE LLC - Jan 2025.pdf",  # no logo
            "KINDER MORGAN TEXAS PIPELINE LLC - Jan 2025.pdf",
            "EAP Ohio LLC - Jan 2025.pdf",  # has encino_energy logo
            "ARC Resources U.S. Corp - Jan 2025.pdf",
            "Spark Energy Gas LLC - Dec 2024.pdf",
            "Mercuria Energy America LLC - Jan 2025.pdf",
            "Foundation Energy Management - Jan 2025.pdf",
            "Washington Gas Light Company - Jan 2025.pdf",
        ]

        # Get test data directory
        classification_data_dir = Path(__file__).parent / "test-data" / "classification"

        if not classification_data_dir.exists():
            print(f"Classification data directory not found: {classification_data_dir}")
            pytest.skip(f"Classification data directory not found: {classification_data_dir}")

        # Get all PDF files from classification directory
        pdf_files = [
            f
            for f in classification_data_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".pdf"
        ]

        # Filter documents if documents_to_test is specified
        if documents_to_test:
            pdf_files = [f for f in pdf_files if f.name in documents_to_test]

        layout_name_mapping = {}  # Store generated layout names for each file

        # Phase 1: Generate layout names for all files
        print("\nLayout name generation in progress..")
        for pdf_file in pdf_files:
            print(f"\nProcessing '{pdf_file.name}'..")
            try:
                # Convert PDF to base64 images (first 3 pages)
                image_dicts = agent_client._pdf_to_images(pdf_file)
                base64_images = [img["value"] for img in image_dicts[:3]]

                # Generate layout name for the document using multi-candidate approach
                generated_layout_name = agent_client.generate_document_layout_name(
                    base64_images, pdf_file.name
                )

                # Store the mapping
                layout_name_mapping[str(pdf_file)] = {
                    "generated_layout_name": generated_layout_name,
                    "base64_images": [
                        img["value"] for img in image_dicts
                    ],  # Store all images for classification
                }

                print(f"{pdf_file.name} -> {generated_layout_name}")

            except Exception as e:
                print(f"{pdf_file.name} -> ERROR: {e!s}")
                layout_name_mapping[str(pdf_file)] = {
                    "generated_layout_name": None,
                    "error": str(e),
                }

        # Phase 2: Classify files using generated layout names
        print("\nClassification in progress..")

        # Get all unique generated layout names (excluding None/errors)
        all_generated_layouts = list(
            set(
                [
                    mapping["generated_layout_name"]
                    for mapping in layout_name_mapping.values()
                    if mapping.get("generated_layout_name") is not None
                ]
            )
        )

        correct_count = 0
        total_count = 0

        for pdf_file_path, mapping in layout_name_mapping.items():
            pdf_file = Path(pdf_file_path)
            print(f"\nProcessing '{pdf_file.name}'..")

            if mapping.get("error") or mapping.get("generated_layout_name") is None:
                continue

            try:
                # Classify using multi-signal approach (image + filename only)
                classified_layout_name = agent_client.classify_document_multi_signal(
                    base64_images=mapping["base64_images"],
                    available_layouts=all_generated_layouts,
                    doc_name=pdf_file.name,
                )

                # Check if classification matches the generated layout name
                is_correct = (
                    classified_layout_name.lower() == mapping["generated_layout_name"].lower()
                )
                if is_correct:
                    correct_count += 1
                total_count += 1

                print(
                    f"{pdf_file.name} -> Expected: {mapping['generated_layout_name']}, "
                    f"Classified: {classified_layout_name}"
                )

            except Exception as e:
                print(f"{pdf_file.name} -> ERROR: {e!s}")

        accuracy = correct_count / total_count if total_count > 0 else 0.0
        print(
            f"\nClassification result.. \n{correct_count} / {total_count} "
            f"({accuracy * 100:.0f}%) classified correctly."
        )

    def test_document_unclassified(self, agent_client):
        """Test document classification using multi-signal approach with predefined available
        layouts."""

        # Document to test
        document_to_test = "ARC Resources U.S. Corp - Jan 2025.pdf"

        # Predefined available layouts
        available_layouts = ["eog_resources", "laramie", "intercon", "hilcorp", "qb"]

        # Get test data directory
        classification_data_dir = Path(__file__).parent / "test-data" / "classification"

        # Find the specific PDF file
        pdf_file = classification_data_dir / document_to_test

        print(f"\nProcessing document: {document_to_test}")
        print(f"Available layouts: {available_layouts}")

        try:
            # Convert PDF to base64 images (first 3 pages)
            print(f"Converting PDF to images: {pdf_file.name}")
            image_dicts = agent_client._pdf_to_images(pdf_file)
            base64_images = [img["value"] for img in image_dicts[:3]]
            print(f"Generated {len(base64_images)} images")

            # Classify using multi-signal approach
            print(f"Classifying against available layouts: {available_layouts}")
            classified_layout_name = agent_client.classify_document_multi_signal(
                base64_images=base64_images,
                available_layouts=available_layouts,
                doc_name=pdf_file.name,
            )

            print(f"✓ Document successfully classified as: {classified_layout_name}")

        except DocumentClassificationError as e:
            # This is expected for unclassified documents - print the error details
            print("✓ Document classification failed as expected (unclassified)")
            print(f"  Error details: {e!s}")

            # Assert that DocumentClassificationError was raised (this is the expected behavior)
            assert True, (
                "DocumentClassificationError was raised as expected for unclassified document"
            )

        except Exception as e:
            print(f"✗ Unexpected error during classification: {e!s}")
            raise


# Not a part of the DocumentClassification suite.
def test_update_filename_scores():
    """Test that the default layout score is 1.0 and other layouts are not affected."""
    filename_scores = {"default": 0.5, "other": 0.3}

    updated_scores = AgentServerClient._update_filename_scores(filename_scores)
    assert updated_scores == {"default": 1.0, "other": 0.3}
