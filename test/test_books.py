from unittest.mock import patch, MagicMock
from app.books import _normalize, search_books, get_book_by_id, is_text_about_author, get_author_info

# ==============================================================================
# Basic Tests
# ==============================================================================
def test_normalize_complete_book():
    """
    Test the normalization of a complete book data structure from API.

    Verifies that the _normalize function correctly extracts and formats
    all book information including title, authors, publisher, ISBN, and
    categories from the Google Books API response format.
    """
    # Mock a complete API response item
    item = {
        "id": "test123",
        "volumeInfo": {
            "title": "Test Book",
            "authors": ["Alice"],
            "publisher": "Test Pub",
            "publishedDate": "2022",
            "description": "Test description",
            "categories": ["Fiction"],
            "industryIdentifiers": [
                {"type": "ISBN_13", "identifier": "1234567890123"}
            ]
        }
    }

    # Normalize the mock data
    book = _normalize(item)

    # Assert all fields are correctly extracted
    assert book["title"] == "Test Book"
    assert book["authors"] == ["Alice"]
    assert book["publisher"] == "Test Pub"
    assert book["isbn"] == "1234567890123"
    assert book["categories"] == ["Fiction"]


def test_search_books_empty_query():
    """
    Test search behavior with an empty query string.

    Ensures that searching with an empty query returns an empty list
    rather than attempting an invalid API call.
    """
    result = search_books("")
    assert result == []


def test_get_book_by_id_fallback():
    """
    Test retrieving a book by ID from the fallback collection.

    Verifies that books with 'fb' prefix IDs (fallback books) can be
    retrieved correctly and contain all required fields.
    """
    # Get the first fallback book
    book = get_book_by_id("fb1")

    # Verify book was found and has required fields
    assert book is not None
    assert book["id"] == "fb1"
    assert "title" in book
    assert "authors" in book


def test_is_text_about_author_success():
    """
    Test that text containing relevant author keywords returns True.
    """
    text = "Jojo Moyes is an English journalist and romance novelist."
    # Should return True because 'novelist' and 'journalist' are in the whitelist
    assert is_text_about_author(text, "Jojo Moyes") is True


def test_is_text_about_author_failure_blocklist():
    """
    Test that text containing blocklisted words (e.g., chemical elements) returns False.
    """
    text = "Lead (Pb) is a chemical element with atomic number 82."
    # Should return False because 'chemical element' is in the blocklist
    assert is_text_about_author(text, "Pb") is False


def test_is_text_about_author_name_mismatch():
    """
    Test that text where the author's name does not appear at the beginning returns False.
    This prevents returning an article about an art movement when searching for a person.
    """
    # Simulate a search for 'Karel Smejkal' returning an art movement description
    text = "Czech Informel is described as a movement of abstract art..."
    # Should return False because 'Karel' is not found in the first 250 characters
    assert is_text_about_author(text, "Karel Smejkal") is False


# ==============================================================================
# Author Fetching Strategy Tests
# ==============================================================================

@patch('app.books.requests.get')
def test_get_author_info_strategy_1_direct_success(mock_get):
    """
    Test Strategy 1: Direct Wikipedia API lookup.

    Scenario:
        - The user searches for a famous author.
        - Wikipedia returns a 200 OK response.
        - The content validation passes.
    """
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'extract': 'J.K. Rowling is a British author famous for Harry Potter.',
        'thumbnail': {'source': 'http://image.url/jk.jpg'}
    }
    mock_get.return_value = mock_response

    # Execute
    result = get_author_info("J.K. Rowling")

    # Assertions
    assert result['source'] == "Wikipedia (Direct)"
    assert "Harry Potter" in result['bio']
    assert result['image'] == 'http://image.url/jk.jpg'


@patch('app.books.wikipedia.search')
@patch('app.books.wikipedia.page')
@patch('app.books.requests.get')
def test_get_author_info_strategy_2_fuzzy(mock_get, mock_wiki_page, mock_wiki_search):
    """
    Test Strategy 2: Direct lookup fails, but Fuzzy Search succeeds.

    Scenario:
        - Strategy 1 (Direct Request) returns a 404 error.
        - Code falls back to Fuzzy Search.
        - Search returns results and validation passes.
    """
    # 1. Mock Strategy 1 (Direct) to fail
    mock_get.return_value.status_code = 404

    # 2. Mock Strategy 2 (Fuzzy) to succeed
    mock_wiki_search.return_value = ["J.K. Rowling"]

    # Mock the page object returned by wikipedia.page()
    mock_page_obj = MagicMock()
    mock_page_obj.summary = "J.K. Rowling is a writer."
    mock_page_obj.images = ["img1.jpg"]
    mock_wiki_page.return_value = mock_page_obj

    result = get_author_info("J.K. Rowling")

    assert result['source'] == "Wikipedia (Fuzzy)"
    assert result['bio'] == "J.K. Rowling is a writer."


@patch('app.books._get_author_from_open_library')
@patch('app.books.wikipedia.search')
@patch('app.books.requests.get')
def test_get_author_info_strategy_3_fallback(mock_get, mock_wiki_search, mock_ol):
    """
    Test Strategy 3: Both Wikipedia strategies fail, Open Library succeeds.
    """
    # 1. Mock Strategy 1 (Direct) to fail
    mock_get.return_value.status_code = 404

    # 2. Mock Strategy 2 (Fuzzy) to fail (no results)
    mock_wiki_search.return_value = []

    # 3. Mock Strategy 3 (Open Library) to succeed
    mock_ol.return_value = {
        "bio": "Bio from Open Library",
        "source": "OpenLibrary",
        "image": "http://ol.org/img.jpg",
        "born": "1990"
    }

    result = get_author_info("Unknown Author")

    assert result['source'] == "OpenLibrary"
    assert result['bio'] == "Bio from Open Library"


@patch('app.books.requests.get')
def test_search_books_api_call(mock_get):
    """
    Test the search_books function with a mocked API response.

    Verifies that the function correctly parses the nested JSON structure.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "id": "123",
                "volumeInfo": {
                    "title": "Mock Book Title",
                    "authors": ["Mock Author"],
                    "publisher": "Mock Publisher",
                    "publishedDate": "2023"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    results = search_books("test query")
    assert len(results) == 1
    assert results[0]['title'] == "Mock Book Title"

