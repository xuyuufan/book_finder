"""
Tests for the recommendation system.

This module tests both content-based and genre-based recommendation
algorithms used to suggest similar books to users.
"""

from app.recommend import content_based_similar,genre_based

def test_content_based_similarity_basic():
    """
        Test basic content-based similarity matching.

        Verifies that the content-based algorithm correctly identifies
        similar books based on title and description text matching.
        Expects the Python programming book to rank higher than the
        unrelated cooking book.
        """
    # Define anchor book (the reference book we're finding similarities for)
    anchors = [{"id": "a1", "title": "Python", "description": "Learn Python"}]
    # Define candidate books to compare against
    candidates = [
        {"id": "b1", "title": "Advanced Python", "description": "Python programming"},
        {"id": "b2", "title": "Cooking", "description": "Food recipes"}
    ]

    # Get top 1 similar book
    result = content_based_similar(anchors, candidates, top_k=1)

    # Verify we got exactly 1 result
    assert len(result) == 1

    # Verify the most similar book is "Advanced Python" (not "Cooking")
    assert result[0]["book"]["id"] == "b1"


def test_content_based_empty_candidates():
    """
    Test content-based similarity with empty candidate list.

    Ensures the algorithm handles edge cases gracefully and returns
    an empty list when there are no candidates to compare against.
    """
    # Call with empty candidate list
    result = content_based_similar([{"id": "a"}], [])
    assert result == [] # Verify empty list is returned


def test_genre_based_grouping():
    """
    Test genre-based book grouping and recommendation.

    Verifies that books are correctly grouped by genre/category
    and that the most populous genre appears first with the
    correct number of books.
    """
    # Define books with different genres
    books = [
        {"id": "1", "categories": ["Fiction"]},
        {"id": "2", "categories": ["Fiction"]},
        {"id": "3", "categories": ["History"]}
    ]

    # Get top 2 books grouped by genre
    result = genre_based(books, top_k=2)
    assert result[0]["genre"] == "Fiction" # Verify Fiction appears first (has 2 books, the most)
    assert len(result[0]["books"]) == 2  # Verify Fiction genre contains 2 books