from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import datetime, random
from .books import search_books, get_daily_book, get_you_might_like, FALLBACK_BOOKS, get_book_by_id, get_author_info
from .recommend import content_based_similar, genre_based

bp = Blueprint('main', __name__)

MAX_API_RESULTS = 40

def clean_title(title):
    """
    Clean and normalize book titles for duplicate detection.

    Removes subtitles (after ':') and edition info (in parentheses),
    then converts to lowercase for consistent comparison.

    Args:
        title (str): The original book title

    Returns:
        str: Cleaned and normalized title
    """
    if not title:
        return ""
    return title.split(':')[0].split('(')[0].strip().lower()


@bp.route('/', methods=['GET'])
def index():
    """
    Render the homepage with various book collections.

    Displays:
    - Popular books by genre
    - Curated love lists (trending, themed collections)
    - Daily featured book
    - Personalized recommendations
    - Calendar widget

    Returns:
        Rendered index.html template with all homepage data
    """

    # 1. Popular this week - fetch books by genre
    genre_queries = {
        'fiction': 'subject:fiction',
        'history': 'subject:history',
        'thriller': 'subject:thriller',
        'scifi': 'subject:science fiction',
        'mystery': 'subject:mystery',
        'fantasy': 'subject:fantasy',
        'biography': 'subject:biography'
    }

    popular_books = {}
    BOOKS_ONLY_FALLBACK = FALLBACK_BOOKS[:30]

    for key, query in genre_queries.items():
        books = search_books(query, max_results=8)
        if not books:
            count = min(len(BOOKS_ONLY_FALLBACK), 8)
            popular_books[key] = random.sample(BOOKS_ONLY_FALLBACK, count)
        else:
            popular_books[key] = books

    # 2. Love lists - curated collections with deduplication
    def get_list_safe(query, fallback_slice, count=5):
        """
         Get a unique list of books, avoiding duplicates by title.

         Args:
             query (str): Search query for books
             fallback_slice (list): Fallback books if query fails
             count (int): Number of unique books to return

         Returns:
             list: Unique books up to the specified count
         """

        res = search_books(query, max_results=25)
        unique_results = []
        seen_titles = set()

        def process_books(source_list):
            """Process book list and add unique titles only."""
            for book in source_list:
                raw_title = book.get('title', '')
                title_key = clean_title(raw_title)

                if title_key not in seen_titles:
                    unique_results.append(book)
                    seen_titles.add(title_key)

                if len(unique_results) >= count:
                    break

        # Try API results first
        if res:
            process_books(res)
        # Fill with fallback books if needed
        if len(unique_results) < count:
            process_books(fallback_slice)

        return unique_results[:count]

    lists_data = {
        'trending': get_list_safe('subject:fiction sort:new', FALLBACK_BOOKS[0:5], count=5),
        'christmas': get_list_safe('subject:christmas', FALLBACK_BOOKS[10:15], count=5),
        'life essentials': get_list_safe('intitle:"The Kite Runner" OR intitle:"The Alchemist" OR intitle:"Life of Pi"',
                                         FALLBACK_BOOKS[0:5], count=5)
    }
    # Get featured and recommended books
    daily_book = get_daily_book() or FALLBACK_BOOKS[0]
    you_might_like_books = get_you_might_like() or FALLBACK_BOOKS[:4]
    tree_books = search_books('subject:fiction "uplifting"', max_results=4) or FALLBACK_BOOKS[:4]

    # Prepare calendar widget data
    now = datetime.datetime.now()
    calendar_data = {'month': now.strftime("%b"), 'day': now.day, 'weekday': now.strftime("%A")}

    return render_template(
        'index.html',
        popular_books=popular_books,
        love_lists=lists_data,
        daily_book=daily_book,
        you_might_like_books=you_might_like_books,
        tree_books=tree_books,
        calendar_data=calendar_data,
    )


@bp.route('/search', methods=['GET', 'POST'])
def search():
    """
    Handle book search requests and display results with recommendations.

    Accepts search queries via GET or POST, fetches matching books,
    and generates content-based and genre-based recommendations.

    Returns:
        Rendered results.html with search results and recommendations
    """
    # Get search query from POST or GET

    if request.method == 'POST':
        q = request.form.get('q', '').strip()
    else:
        q = request.args.get('q', '').strip()

    page = request.args.get('page', 1, type=int)

    if not q:
        flash("Please enter a search query")
        return redirect(url_for('main.index'))

    # Fetch books from API
    full_search_results = search_books(q, max_results=MAX_API_RESULTS, page=page)

    if not full_search_results:
        return render_template('results.html', q=q, books=[], recommendations={}, page=page)

    # Split results: first 12 for display, rest for recommendations
    query_display_books = full_search_results[:12]
    recommendation_pool_books = full_search_results[12:]

    # Generate recommendations
    similar_books = content_based_similar(query_display_books, recommendation_pool_books, top_k=5)
    genre_recommendations = genre_based(recommendation_pool_books, top_k=5)

    recommendations = {
        "similar_books": similar_books,
        "genre_recommendations": genre_recommendations
    }

    return render_template('results.html', q=q, books=query_display_books, recommendations=recommendations, page=page)


@bp.route('/genre/<genre>')
def search_genre(genre):
    """
    Search and display books by genre.

    Args:
        genre (str): Genre name to search for

    Returns:
        Rendered results.html with genre-specific books and recommendations
    """

    page = request.args.get('page', 1, type=int)
    q = f"subject:{genre}"

    # Try genre-specific search first
    full_search_results = search_books(q, max_results=MAX_API_RESULTS, page=page)

    # Fallback to general search if no results
    if not full_search_results:
        full_search_results = search_books(genre, max_results=MAX_API_RESULTS, page=page)

    if not full_search_results:
        return render_template('results.html', q=genre, books=[], recommendations={}, page=page)

    # Split results for display and recommendations
    query_display_books = full_search_results[:12]
    recommendation_pool_books = full_search_results[12:]

    # Generate recommendations
    similar_books = content_based_similar(query_display_books, recommendation_pool_books, top_k=4)
    genre_recommendations = genre_based(recommendation_pool_books, top_k=4)

    recommendations = {
        "similar_books": similar_books,
        "genre_recommendations": genre_recommendations
    }

    return render_template('results.html', q=genre, books=query_display_books, recommendations=recommendations,
                           page=page)


@bp.route('/book/<book_id>')
def book_detail(book_id):
    """
    Display detailed information about a specific book.

    Features:
    - Book information and description
    - Similar book recommendations
    - Recently viewed books (with deduplication)
    - View history tracking

    Args:
        book_id (str): Unique identifier for the book

    Returns:
        Rendered book_detail.html with book info and recommendations
    """

    book = get_book_by_id(book_id)

    if not book:
        flash("Book not found or API error.")
        return redirect(url_for('main.index'))

    # Initialize session data if needed
    if 'viewed_books' not in session:
        session['viewed_books'] = []
    if 'hidden_books' not in session:
        session['hidden_books'] = []

    # Update view history (move current book to front)
    viewed = session['viewed_books']
    if book_id in viewed:
        viewed.remove(book_id)
    viewed.insert(0, book_id)
    if len(viewed) > 10:
        viewed = viewed[:10]
    session['viewed_books'] = viewed
    session.modified = True

    # Generate recommendations based on book's genre
    recommendations = []
    if book.get('categories'):
        genre_query = f"subject:{book['categories'][0]}"
        candidate_pool = search_books(genre_query, max_results=20)
        hidden_list = session.get('hidden_books', [])
        candidate_pool = [b for b in candidate_pool if b['id'] != book['id'] and b['id'] not in hidden_list]
        similar_items = content_based_similar([book], candidate_pool, top_k=6)
        recommendations = [item['book'] for item in similar_items]

    # Use fallback if no recommendations generated
    if not recommendations:
        recommendations = FALLBACK_BOOKS[:6]

    # Build recently viewed list with deduplication
    recently_viewed_objs = []
    seen_history_titles = set()
    current_title_key = clean_title(book['title'])
    seen_history_titles.add(current_title_key)

    for vid in session['viewed_books']:
        v_book = get_book_by_id(vid)
        if v_book:
            t_key = clean_title(v_book['title'])
            if t_key not in seen_history_titles:
                recently_viewed_objs.append(v_book)
                seen_history_titles.add(t_key)
            if len(recently_viewed_objs) >= 6:
                break

    return render_template('book_detail.html', book=book, recommendations=recommendations,
                           recently_viewed=recently_viewed_objs)


@bp.route('/hide_book/<book_id>', methods=['POST'])
def hide_book(book_id):
    """
    Hide a book from recommendations and search results.

    Adds the book ID to the user's hidden books list in session.

    Args:
        book_id (str): ID of the book to hide

    Returns:
        JSON response indicating success
    """
    if 'hidden_books' not in session:
        session['hidden_books'] = []
    hidden = session['hidden_books']
    if book_id not in hidden:
        hidden.append(book_id)
        session['hidden_books'] = hidden
        session.modified = True
    return jsonify({"success": True, "message": "Book hidden"})


@bp.route('/remove_history/<book_id>', methods=['POST'])
def remove_history(book_id):
    """
    Remove a book from the viewing history.

    Deletes the specified book ID from the user's viewed books list.

    Args:
        book_id (str): ID of the book to remove from history

    Returns:
        JSON response indicating success
    """
    if 'viewed_books' in session:
        viewed = session['viewed_books']
        if book_id in viewed:
            viewed.remove(book_id)
            session['viewed_books'] = viewed
            session.modified = True
    return jsonify({"success": True, "message": "Removed from history"})


@bp.route('/author/<author_name>')
def author_detail(author_name):
    """
    Display detailed information about an author.

    Shows:
    - Author biography and photo
    - List of their books
    - Statistics (total pages, years active, top genres)

    Args:
        author_name (str): Name of the author

    Returns:
        Rendered author_detail.html with author info and books
    """
    # Initialize author data structure
    author_data = {
        "name": author_name,
        "bio": None,
        "image": None,
        "born": "N/A",
        "genres": []
    }

    # Fetch author information from unified API
    info = get_author_info(author_name)
    if info:
        author_data.update(info)

    # Apply fallback values
    if not author_data['bio']:
        author_data['bio'] = "Biography not available at the moment."

    if not author_data['image']:
        author_data['image'] = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    # Fetch author's books
    author_books = search_books(f'inauthor:"{author_name}"', max_results=12)

    # Calculate statistics
    stats = {
        "total_pages": 0,
        "years_active": [],
        "top_genres": []
    }

    genre_counts = {}

    if author_books:
        for book in author_books:
            # Sum total pages
            stats["total_pages"] += book.get('pageCount', 0)

            # Collect publication years
            pub_date = book.get('publishedDate', '')
            if pub_date and len(pub_date) >= 4:
                try:
                    year = int(pub_date[:4])
                    stats["years_active"].append(year)
                except:
                    pass

            # Count genres
            for genre in book.get('categories', []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    # Determine years active range
    if stats["years_active"]:
        stats["years_range"] = f"{min(stats['years_active'])} - {max(stats['years_active'])}"
    else:
        stats["years_range"] = "N/A"

    # Get top 4 genres by count
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    stats["top_genres"] = [g[0] for g in sorted_genres[:4]]

    return render_template('author_detail.html', author=author_data, books=author_books, stats=stats)


@bp.route('/advanced_search')
def advanced_search():
    """
    Display the advanced search form.

    Returns:
        Rendered advanced_search.html template
    """
    return render_template('advanced_search.html')


@bp.route('/advanced_search_results')
def advanced_search_results():
    """
    Process advanced search form and redirect to results.

    Accepts multiple search parameters (title, author, publisher, ISBN, keywords)
    and constructs a combined search query.

    Returns:
        Redirect to main search route with constructed query
    """
    # Get all search parameters
    title = request.args.get('title', '').strip()
    author = request.args.get('author', '').strip()
    publisher = request.args.get('publisher', '').strip()
    isbn = request.args.get('isbn', '').strip()
    keywords = request.args.get('keywords', '').strip()

    # Build query parts
    query_parts = []
    if title: query_parts.append(f'intitle:{title}')
    if author: query_parts.append(f'inauthor:{author}')
    if publisher: query_parts.append(f'inpublisher:{publisher}')
    if isbn: query_parts.append(f'isbn:{isbn}')
    if keywords: query_parts.append(keywords)

    # Require at least one field
    if not query_parts:
        flash("Please fill in at least one field.")
        return redirect(url_for('main.advanced_search'))

    # Combine all parts and redirect to search
    full_query = " ".join(query_parts)
    return redirect(url_for('main.search', q=full_query))


@bp.route('/feeling_lucky')
def feeling_lucky():
    """
    Redirect to a random book detail page.

    Selects a random book from the fallback collection
    for a serendipitous discovery experience.

    Returns:
        Redirect to book_detail page of a random book
    """
    lucky_book = random.choice(FALLBACK_BOOKS)
    book_id = lucky_book['id']
    return redirect(url_for('main.book_detail', book_id=book_id))