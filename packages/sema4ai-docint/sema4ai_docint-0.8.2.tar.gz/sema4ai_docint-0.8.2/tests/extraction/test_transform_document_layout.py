from sema4ai_docint.extraction.transform.transform_document_layout import (
    TransformDocumentLayout,
)


class TestTransformDocumentLayout:
    def test_tokens(self):
        # Test path tokenization
        path = "pages[*].blocks[*].text"
        tokens = TransformDocumentLayout.tokens(path)
        assert tokens == ["pages[*]", "blocks[*]", "text"]

    def test_collect(self):
        # Test collecting values from nested structure
        doc = {
            "pages": [
                {"blocks": [{"text": "Hello"}, {"text": "World"}]},
                {"blocks": [{"text": "Test"}]},
            ]
        }

        # Test collecting all text values
        texts = TransformDocumentLayout.collect(doc, ["pages[*]", "blocks[*]", "text"])
        assert texts == ["Hello", "World", "Test"]

        # Test collecting single value
        page = TransformDocumentLayout.collect(doc, ["pages[*]"])
        assert len(page) == 2

    def test_set_path(self):
        # Test setting nested path
        root = {}
        TransformDocumentLayout.set_path(root, "metadata.title", "Test Document")
        assert root["metadata"]["title"] == "Test Document"

    def test_cast(self):
        # Test various type casting scenarios
        assert TransformDocumentLayout.cast("123", "int") == 123
        assert TransformDocumentLayout.cast("1,234.56", "float") == 1234.56
        assert TransformDocumentLayout.cast("$ 1,234.56", "float") == 1234.56
        assert TransformDocumentLayout.cast("yes", "bool")
        assert not TransformDocumentLayout.cast("no", "bool")
        assert TransformDocumentLayout.cast(123, "str") == "123"

    def test_flatten(self):
        # Test flattening nested document structure
        doc = {
            "metadata": {"title": "Test Doc"},
            "pages": [
                {
                    "number": 1,
                    "blocks": [
                        {"text": "Hello", "confidence": 0.9},
                        {"text": "World", "confidence": 0.8},
                    ],
                }
            ],
        }

        # Test flattening with relative paths
        extras = {"page_num": "../number", "doc_title": "../../metadata.title"}

        flattened = TransformDocumentLayout.flatten(
            doc, TransformDocumentLayout.tokens("pages[*].blocks[*]"), extras
        )

        # Verify the structure of flattened results
        assert len(flattened) == 2

        # Check first block
        assert flattened[0]["text"] == "Hello"
        assert flattened[0]["confidence"] == 0.9
        assert flattened[0]["page_num"] == 1
        assert flattened[0]["doc_title"] == "Test Doc"

        # Check second block
        assert flattened[1]["text"] == "World"
        assert flattened[1]["confidence"] == 0.8
        assert flattened[1]["page_num"] == 1
        assert flattened[1]["doc_title"] == "Test Doc"
