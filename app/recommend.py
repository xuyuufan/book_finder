import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple, Set

# Define data structure types
Book = Dict[str, Any]
RecommendedBook = Dict[str, Any]

# Similarity threshold: prevents recommending books with extremely low, irrelevant scores
SIMILARITY_THRESHOLD = 0.05


def _create_corpus(books: List[Book]) -> List[str]:
    """
    Converts the list of books into a corpus for TF-IDF calculation.
    Concatenates title, authors, and description as the book's content representation.
    """
    corpus = []
    for book in books:
        # Robustly retrieve fields, use an empty string if missing
        title = book.get('title', '')
        authors = ' '.join(book.get('authors', []))
        description = book.get('description', '')
        categories = ' '.join(book.get('categories', []))
        publisher = book.get('publisher', '')
        published_date = book.get('publishedDate', '')
        # Concatenate into a single large text string
        text = f"{title} {authors} {categories} {publisher} {published_date} {description}"
        corpus.append(text.strip())
    return corpus


def content_based_similar(
        anchor_books: List[Book],  # S_Query Display: The first N books displayed in the search results (Anchor set)
        candidate_books: List[Book],  # S_Recommendation Pool: Books starting from N+1 (Candidate set)
        top_k: int = 5
) -> List[RecommendedBook]:
    """
    Implements multi-anchor aggregation recommendation (Content-Based Similar).
    Calculates the similarity of each anchor to all books in the candidate pool, and aggregates scores for sorting.

    Args:
    - anchor_books: Anchor list for similarity calculation (A module's query_display_books)
    - candidate_books: Candidate pool for recommendations (A module's recommendation_pool_books)
    - top_k: Number of recommendations to return
    """
    if not anchor_books or not candidate_books:
        if not anchor_books or not candidate_books:
            print("Anchor or candidate book list is empty.")
            return []

        print(f"Anchor books: {len(anchor_books)}")
        print(f"Candidate books: {len(candidate_books)}")
        return []

    # Build a unified corpus and perform TF-IDF vectorization
    # All books must be vectorized to ensure they are in the same feature space
    all_books = anchor_books + candidate_books
    corpus = _create_corpus(all_books)

    print("First 3 corpus samples:")
    for text in corpus[:3]:
        print(text[:120])

    vectorizer = vectorizer = TfidfVectorizer(max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Return empty list if the corpus is empty
        return []

    # Split matrix: Anchor vectors and Candidate vectors
    num_anchors = len(anchor_books)
    anchor_vectors = tfidf_matrix[:num_anchors]
    candidate_vectors = tfidf_matrix[num_anchors:]

    # 2. Calculate similarity and aggregate scores (Implement multi-anchor voting)
    aggregated_scores = {}
    candidate_map = {book['id']: book for book in candidate_books}  # Used to look up the book object by ID

    # Iterate through each anchor (each book in the query results)
    for anchor_vector in anchor_vectors:
        # Calculate the similarity between this anchor and all candidate books
        # The result is an array with a number of elements equal to candidate_vectors
        cosine_sims = cosine_similarity(anchor_vector, candidate_vectors).flatten()

        # Aggregate scores
        for j, score in enumerate(cosine_sims):
            # Filter out noise results below the threshold
            if score < SIMILARITY_THRESHOLD:
                continue

            book_id = candidate_books[j]["id"]

            # Aggregation: accumulate the similarity score calculated by this anchor into the book's total score
            # Books recommended by multiple anchors will receive a higher aggregated score
            aggregated_scores[book_id] = aggregated_scores.get(book_id, 0.0) + score

    # 3. Sort and format output

    # Sort by aggregated score in descending order
    sorted_recommendations = sorted(
        aggregated_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Build the final recommendation list, taking only Top-K
    recommendations = []
    for book_id, score in sorted_recommendations[:top_k]:
        recommendations.append({
            "score": round(float(score), 4),  # The score here is the aggregated score
            "book": candidate_map[book_id]
        })

    return recommendations


def genre_based(books: List[Book], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Genre-based recommendation: groups the input list of books by category and returns the Top-K genres.

    Optimizations:
    1. Uses a Set to ensure deduplication of books in the final recommendation list.
    2. Sorts based on the number of books in the category to implement genre aggregation.

    Args:
    - books: The list of books used for categorization (A module's recommendation_pool_books)
    - top_k: The number of top categories to return
    """
    if not books:
        return []

    genre_counts: Dict[str, List[Book]] = {}

    # 1. Count and aggregate books for each category
    for book in books:
        # Assumes Module B stores categories in the 'categories' list
        categories = book.get('categories', [])

        # Simply take the first category as the primary category for statistics
        if categories:
            genre = categories[0]
            if genre not in genre_counts:
                # Stores the list of books under this category
                genre_counts[genre] = []
            genre_counts[genre].append(book)

    # 2. Sort by the number of books in the category in descending order (implements genre aggregation)
    # Categories with more books are more likely to be selected by multiple anchor books, thus ranking higher
    sorted_genres = sorted(
        genre_counts.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    # 3. Build the final genre recommendation list, ensuring book deduplication
    genre_recommendations = []
    recommended_book_ids: Set[str] = set()  # Used to store the IDs of already recommended books to ensure deduplication

    # Iterate through the Top-K sorted genres
    for genre, book_list in sorted_genres[:top_k]:

        # Collect books in this category that haven't been recommended yet
        unique_books_for_genre = []
        for book in book_list:
            book_id = book.get('id')
            if book_id and book_id not in recommended_book_ids:
                unique_books_for_genre.append(book)
                # Add the book ID to the set of recommended IDs
                recommended_book_ids.add(book_id)

        if unique_books_for_genre:
            genre_recommendations.append({
                "genre": genre,
                # Limit each category to display only the first 3 books (to avoid long lists)
                "books": unique_books_for_genre[:3]
            })

    return genre_recommendations
