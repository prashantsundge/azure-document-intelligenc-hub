from app.services.azure_search import chunk_text


def test_chunk_text_returns_empty_list_for_empty_text() -> None:
    assert chunk_text("") == []


def test_chunk_text_returns_one_chunk_for_short_text() -> None:
    text = "Northstar provides a laptop and monitor."
    assert chunk_text(text) == [text]


def test_chunk_text_splits_long_text_with_overlap() -> None:
    words = [f"word{number}" for number in range(1, 31)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=10, overlap=2)

    assert len(chunks) == 4
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]
    assert chunks[1].split()[-2:] == chunks[2].split()[:2]