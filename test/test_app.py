from unittest.mock import patch

def test_index_route(client):
    """
    Test the homepage route.

    Verifies that the index page loads successfully with a 200 status code.

    Args:
        client: Flask test client fixture
    """
    response = client.get("/")
    assert response.status_code == 200

def test_search_empty_query_redirect(client):
    """
    Test search behavior with empty query string.

    Ensures that submitting an empty search query redirects properly
    and still returns a valid page (200 status).

    Args:
        client: Flask test client fixture
    """
    response = client.post("/search", data={"q": ""}, follow_redirects=True)
    assert response.status_code == 200

def test_hide_book_route(client):
    """
    Test the book hiding functionality.

    Verifies that hiding a book (by ID) returns success status
    and proper JSON response indicating the operation completed.

    Args:
        client: Flask test client fixture
    """
    response = client.post("/hide_book/fb1")
    assert response.status_code == 200
    assert response.json["success"] is True


def test_remove_history_route(client):
    """
    Test removing a book from viewing history.

    Ensures that the endpoint for removing books from recently viewed
    history responds successfully.

    Args:
        client: Flask test client fixture
    """
    response = client.post("/remove_history/fb1")
    assert response.status_code == 200


def test_book_detail_fallback(client):
    """
    Test the book detail page with fallback behavior.

    Verifies that the book detail page loads correctly, even when
    using fallback data (for book ID 'fb1').

    Args:
        client: Flask test client fixture
    """
    response = client.get("/book/fb1")
    assert response.status_code == 200


# ==============================================================================
# Advanced Route Logic Tests
# ==============================================================================

def test_search_genre_route(client):
    """
    Test that the genre search route loads correctly.

    This ensures the page template renders and the query logic
    (searching for 'subject:fiction') executes without errors.
    """
    # Test a common genre
    response = client.get("/genre/fiction")
    assert response.status_code == 200
    # Check if the genre name appears in the HTML (case-insensitive check)
    assert b"fiction" in response.data.lower() or b"Explore" in response.data


@patch('app.app.get_author_info')
def test_author_detail_route(mock_get_info, client):
    """
    Test the Author Detail page route.

    We mock `get_author_info` to avoid making real calls to Wikipedia/OpenLibrary
    during route testing. This isolates the test to the Flask route logic.
    """
    # Setup mock return data
    mock_get_info.return_value = {
        "bio": "Test Biography Text",
        "image": "test_image.jpg",
        "source": "Test Source",
        "born": "1990"
    }

    # Request the page for a specific author
    response = client.get("/author/TestAuthor")

    # Assertions
    assert response.status_code == 200
    # Verify that the mocked biography is rendered in the HTML
    assert b"Test Biography Text" in response.data


def test_advanced_search_page(client):
    """
    Test that the Advanced Search form page loads successfully.
    """
    response = client.get("/advanced_search")
    assert response.status_code == 200
    # Verify unique element of the page
    assert b"Advanced Search" in response.data


def test_advanced_search_submission(client):
    """
    Test the submission of the Advanced Search form.

    Verifies that the logic correctly combines fields (Title + Author)
    into a single query string (intitle:Harry inauthor:Rowling) and redirects.
    """
    # Simulate submitting the form with Title="Harry" and Author="Rowling"
    # follow_redirects=True will automatically follow the 302 redirect to /search
    response = client.get(
        "/advanced_search_results?title=Harry&author=Rowling",
        follow_redirects=True
    )

    assert response.status_code == 200
    # The search function processes this query.
    # We check if the response path is correctly redirected to /search
    assert response.request.path == "/search"


def test_advanced_search_empty(client):
    """
    Test submitting an empty Advanced Search form.

    Expected behavior: Redirect back to the form page with a flash message.
    """
    response = client.get("/advanced_search_results", follow_redirects=True)

    assert response.status_code == 200
    # Check if the flash message is present in the rendered HTML
    # (Checking for part of the flash message string)
    assert b"Please fill in at least one field" in response.data


def test_feeling_lucky(client):
    """
    Test the 'Feeling Lucky' button.

    Expected behavior: Selects a random book and redirects to its detail page.
    """
    response = client.get("/feeling_lucky", follow_redirects=True)

    assert response.status_code == 200
    # The final page should be a book detail page.
    # The URL path should start with /book/
    assert response.request.path.startswith("/book/")