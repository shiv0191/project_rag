from pathlib import Path

import pytest

from loaders.layout_pdf_parser import (
    parse_pdf_to_documents,
)


PDF_PATH = Path(
    "data/"
    "ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-"
    "for-the-prevention-detection-evaluation-and-management-of.pdf"
)


@pytest.fixture(scope="module")
def documents():
    return parse_pdf_to_documents(
        PDF_PATH
    )


def get_page_text(
    documents,
    page_number: int,
    content_type: str = "page_body",
) -> str:
    matching = [
        document.page_content
        for document in documents
        if (
            document.metadata.get(
                "page_number"
            )
            == page_number
            and document.metadata.get(
                "content_type"
            )
            == content_type
        )
    ]

    return "\n".join(matching)


def test_page_6_section_order(
    documents,
):
    text = get_page_text(
        documents,
        page_number=6,
    )

    assert text

    pos_14 = text.find(
        "1.4. Peer Review Committee"
    )

    pos_15 = text.find(
        "1.5."
    )

    pos_16 = text.find(
        "1.6."
    )

    pos_2 = text.find(
        "2. DEFINITIONS AND CLASSIFICATION"
    )

    assert pos_14 != -1
    assert pos_15 != -1
    assert pos_16 != -1
    assert pos_2 != -1

    assert (
        pos_14
        < pos_15
        < pos_16
        < pos_2
    )


def test_page_11_body_continuity(
    documents,
):
    body_text = get_page_text(
        documents,
        page_number=11,
    )

    assert body_text

    assert (
        "dysfunctional adiposity"
        in body_text
    )

    # Figure caption should not be injected into body.
    assert (
        "FIGURE 1 Stages of CKM Syndrome"
        not in body_text
    )


def test_page_11_figure_is_separate(
    documents,
):
    figure_text = get_page_text(
        documents,
        page_number=11,
        content_type="figure_caption",
    )

    assert figure_text

    assert (
        "FIGURE 1"
        in figure_text
    )


def test_all_documents_have_page_metadata(
    documents,
):
    missing = [
        document
        for document in documents
        if document.metadata.get(
            "page_number"
        )
        is None
    ]

    assert not missing

