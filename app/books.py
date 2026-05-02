import os, requests, datetime, random
import wikipedia
from urllib.parse import urlencode
from .cache import get_from_cache, save_to_cache

# FALLBACK DATA (Defines to avoid circular imports)
FALLBACK_BOOKS = [
    # Top 10 Modern Hits (0-9)
    {
        "id": "fb1",
        "title": "The Invisible Life of Addie LaRue",
        "authors": ["V.E. Schwab"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780765387561-M.jpg",
        "publishedDate": "2020",
        "isbn": "9780765387561",
        "publisher": "Tor Books",
        "pageCount": 448,
        "categories": ["Fantasy", "Historical Fiction", "Romance"],
        "description": "France, 1714: in a moment of desperation, a young woman makes a Faustian bargain to live forever—and is cursed to be forgotten by everyone she meets. Thus begins the extraordinary life of Addie LaRue, and a dazzling adventure that will play out across centuries and continents, across history and art, as a young woman learns how far she will go to leave her mark on the world."
    },
    {
        "id": "fb2",
        "title": "Project Hail Mary",
        "authors": ["Andy Weir"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780593135204-M.jpg",
        "publishedDate": "2021",
        "isbn": "9780593135204",
        "publisher": "Ballantine Books",
        "pageCount": 496,
        "categories": ["Science Fiction", "Thriller", "Space"],
        "description": "Ryland Grace is the sole survivor on a desperate, last-chance mission—and if he fails, humanity and the earth itself will perish. Except that right now, he doesn't know that. He can't even remember his own name, let alone the nature of his assignment or how to complete it. All he knows is that he's been asleep for a very, very long time. And he's just been awakened to find himself millions of miles from home, with nothing but two corpses for company."
    },
    {
        "id": "fb3",
        "title": "The House in the Cerulean Sea",
        "authors": ["T.J. Klune"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781250217318-M.jpg",
        "publishedDate": "2020",
        "isbn": "9781250217318",
        "publisher": "Tor Books",
        "pageCount": 394,
        "categories": ["Fantasy", "LGBTQ+", "Romance"],
        "description": "A magical island. A dangerous task. A burning secret. Linus Baker leads a quiet, solitary life. At forty, he lives in a tiny house with a devious cat and his old records. As a Case Worker at the Department in Charge Of Magical Youth, he spends his days overseeing the well-being of children in government-sanctioned orphanages. When Linus is unexpectedly summoned by Extremely Upper Management he's given a curious and highly classified assignment: travel to Marsyas Island Orphanage, where six dangerous children reside."
    },
    {
        "id": "fb4",
        "title": "The Midnight Library",
        "authors": ["Matt Haig"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780525559474-M.jpg",
        "publishedDate": "2020",
        "isbn": "9780525559474",
        "publisher": "Viking",
        "pageCount": 304,
        "categories": ["Fiction", "Fantasy", "Contemporary"],
        "description": "Between life and death there is a library, and within that library, the shelves go on forever. Every book provides a chance to try another life you could have lived. To see how things would be if you had made other choices . . . Would you have done anything different, if you had the chance to undo your regrets?"
    },
    {
        "id": "fb5",
        "title": "I'm Glad My Mom Died",
        "authors": ["Jennette McCurdy"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781982185824-M.jpg",
        "publishedDate": "2022",
        "isbn": "9781982185824",
        "publisher": "Simon & Schuster",
        "pageCount": 320,
        "categories": ["Memoir", "Nonfiction", "Mental Health"],
        "description": "A heartbreaking and hilarious memoir by iCarly and Sam & Cat star Jennette McCurdy about her struggles as a former child actor—including eating disorders, addiction, and a complicated relationship with her overbearing mother—and how she retook control of her life."
    },
    {
        "id": "fb6",
        "title": "Fourth Wing",
        "authors": ["Rebecca Yarros"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781649374042-M.jpg",
        "publishedDate": "2023",
        "isbn": "9781649374042",
        "publisher": "Red Tower Books",
        "pageCount": 528,
        "categories": ["Fantasy", "Romance", "New Adult"],
        "description": "Twenty-year-old Violet Sorrengail was supposed to enter the Scribe Quadrant, living a quiet life among books and history. Now, the commanding general—also known as her tough-as-talons mother—has ordered Violet to join the hundreds of candidates striving to become the elite of Navarre: dragon riders."
    },
    {
        "id": "fb7",
        "title": "The Ballad of Songbirds and Snakes",
        "authors": ["Suzanne Collins"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781338635171-M.jpg",
        "publishedDate": "2020",
        "isbn": "9781338635171",
        "publisher": "Scholastic Press",
        "pageCount": 517,
        "categories": ["Young Adult", "Dystopian", "Fantasy"],
        "description": "It is the morning of the reaping that will kick off the tenth annual Hunger Games. In the Capitol, eighteen-year-old Coriolanus Snow is preparing for his one shot at glory as a mentor in the Games. The once-mighty house of Snow has fallen on hard times, its fate hanging on the slender chance that Coriolanus will be able to outcharm, outwit, and outmaneuver his fellow students to mentor the winning tribute."
    },
    {
        "id": "fb8",
        "title": "Piranesi",
        "authors": ["Susanna Clarke"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781635575637-M.jpg",
        "publishedDate": "2020",
        "isbn": "9781635575637",
        "publisher": "Bloomsbury Publishing",
        "pageCount": 245,
        "categories": ["Fantasy", "Mystery", "Fiction"],
        "description": "Piranesi's house is no ordinary building: its rooms are infinite, its corridors endless, its walls are lined with thousands upon thousands of statues, each one different from all the others. Within the labyrinth of halls an ocean is imprisoned; waves thunder up staircases, rooms are flooded in an instant. But Piranesi is not afraid; he understands the tides as he understands the pattern of the labyrinth itself."
    },
    {
        "id": "fb9",
        "title": "Lessons in Chemistry",
        "authors": ["Bonnie Garmus"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780385547345-M.jpg",
        "publishedDate": "2022",
        "isbn": "9780385547345",
        "publisher": "Doubleday",
        "pageCount": 400,
        "categories": ["Historical Fiction", "Feminism", "Humor"],
        "description": "Chemist Elizabeth Zott is not your average woman. In fact, Elizabeth Zott would be the first to point out that there is no such thing as an average woman. But it's the early 1960s and her all-male team at Hastings Research Institute takes a very unscientific view of equality. Except for one: Calvin Evans; the lonely, brilliant, Nobel–prize nominated grudge-holder who falls in love with—of all things—her mind. True chemistry results."
    },
    {
        "id": "fb10",
        "title": "Tomorrow, and Tomorrow, and Tomorrow",
        "authors": ["Gabrielle Zevin"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780593321201-M.jpg",
        "publishedDate": "2022",
        "isbn": "9780593321201",
        "publisher": "Knopf",
        "pageCount": 401,
        "categories": ["Fiction", "Contemporary", "Romance"],
        "description": "Sam Masur and Sadie Green. They were often in love, but never lovers. Then they break, and the world breaks them, and the world builds them back up again. A novel about the beauty and resilience of the human spirit, Tomorrow, and Tomorrow, and Tomorrow is a dazzling and intricate examination of the nature of identity, disability, failure, the redemptive possibilities in play, and above all, our need to connect: to be loved and to love."
    },

    # Christmas/Winter (10-14)
    {
        "id": "fb11",
        "title": "A Christmas Carol",
        "authors": ["Charles Dickens"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780141324524-M.jpg",
        "publishedDate": "1843",
        "isbn": "9780141324524",
        "publisher": "Penguin Classics",
        "pageCount": 104,
        "categories": ["Classics", "Fiction", "Holiday"],
        "description": "A Christmas Carol is a novella by Charles Dickens, first published in London by Chapman & Hall in 1843. The story tells of sour and stingy Ebenezer Scrooge's transformation after the supernatural visits of Jacob Marley and the Ghosts of Christmas Past, Present, and Yet to Come."
    },
    {
        "id": "fb12",
        "title": "The Polar Express",
        "authors": ["Chris Van Allsburg"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780544580145-M.jpg",
        "publishedDate": "1985",
        "isbn": "9780544580145",
        "publisher": "Houghton Mifflin Harcourt",
        "pageCount": 32,
        "categories": ["Childrens", "Christmas", "Picture Book"],
        "description": "A young boy, lying awake one Christmas Eve, is welcomed aboard a magical train to the North Pole. The Polar Express makes its way to the city atop the world, where the boy will make his Christmas wish."
    },
    {
        "id": "fb13",
        "title": "How the Grinch Stole Christmas!",
        "authors": ["Dr. Seuss"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780394800790-M.jpg",
        "publishedDate": "1957",
        "isbn": "9780394800790",
        "publisher": "Random House",
        "pageCount": 64,
        "categories": ["Childrens", "Picture Book", "Fiction"],
        "description": "Every Who down in Who-ville liked Christmas a lot . . . but the Grinch, who lived just north of Who-ville, did NOT! Not since 'Twas the night before Christmas' has the beginning of a Christmas tale been so instantly recognizable."
    },
    {
        "id": "fb14",
        "title": "Hercule Poirot's Christmas",
        "authors": ["Agatha Christie"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780062073938-M.jpg",
        "publishedDate": "1938",
        "isbn": "9780062073938",
        "publisher": "HarperCollins",
        "pageCount": 336,
        "categories": ["Mystery", "Crime", "Fiction"],
        "description": "It is Christmas Eve. The Lee family reunion is shattered by a deafening crash of furniture, followed by a high-pitched wailing scream. Upstairs, the tyrannical Simeon Lee lies dead in a pool of blood, his throat slashed. When Hercule Poirot offers to assist, he finds an atmosphere not of mourning but of mutual suspicion."
    },
    {
        "id": "fb15",
        "title": "Wintering",
        "authors": ["Katherine May"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780593189481-M.jpg",
        "publishedDate": "2020",
        "isbn": "9780593189481",
        "publisher": "Riverhead Books",
        "pageCount": 256,
        "categories": ["Nonfiction", "Memoir", "Self Help"],
        "description": "An intimate, revelatory book exploring the ways we can care for and repair ourselves when life knocks us down. Sometimes you slip through the cracks: unforeseen circumstances like an abrupt illness, the death of a loved one, a break up, or a job loss can derail a life."
    },

    # Classics (15-19)
    {
        "id": "fb16",
        "title": "1984",
        "authors": ["George Orwell"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780451524935-M.jpg",
        "publishedDate": "1949",
        "isbn": "9780451524935",
        "publisher": "Signet Classics",
        "pageCount": 328,
        "categories": ["Classics", "Fiction", "Science Fiction"],
        "description": "Among the seminal texts of the 20th century, Nineteen Eighty-Four is a rare work that grows more haunting as its futuristic purgatory becomes more real. Published in 1949, the book offers political satirist George Orwell's nightmarish vision of a totalitarian, bureaucratic world and one poor stiff's attempt to find individuality."
    },
    {
        "id": "fb17",
        "title": "To Kill a Mockingbird",
        "authors": ["Harper Lee"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780061120084-M.jpg",
        "publishedDate": "1960",
        "isbn": "9780061120084",
        "publisher": "Harper Perennial Modern Classics",
        "pageCount": 324,
        "categories": ["Classics", "Fiction", "Historical"],
        "description": "The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it, To Kill A Mockingbird became both an instant bestseller and a critical success when it was first published in 1960. It went on to win the Pulitzer Prize in 1961."
    },
    {
        "id": "fb18",
        "title": "The Great Gatsby",
        "authors": ["F. Scott Fitzgerald"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780743273565-M.jpg",
        "publishedDate": "1925",
        "isbn": "9780743273565",
        "publisher": "Scribner",
        "pageCount": 180,
        "categories": ["Classics", "Fiction", "Romance"],
        "description": "The Great Gatsby, F. Scott Fitzgerald's third book, stands as the supreme achievement of his career. This exemplary novel of the Jazz Age has been acclaimed by generations of readers. The story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan."
    },
    {
        "id": "fb19",
        "title": "Pride and Prejudice",
        "authors": ["Jane Austen"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781503290563-M.jpg",
        "publishedDate": "1813",
        "isbn": "9781503290563",
        "publisher": "CreateSpace Independent Publishing Platform",
        "pageCount": 279,
        "categories": ["Classics", "Romance", "Fiction"],
        "description": "Since its immediate success in 1813, Pride and Prejudice has remained one of the most popular novels in the English language. Jane Austen called this brilliant work 'her own darling child' and its vivacious heroine, Elizabeth Bennet, 'as delightful a creature as ever appeared in print.'"
    },
    {
        "id": "fb20",
        "title": "Sapiens",
        "authors": ["Yuval Noah Harari"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780062316097-M.jpg",
        "publishedDate": "2011",
        "isbn": "9780062316097",
        "publisher": "Harper",
        "pageCount": 443,
        "categories": ["Nonfiction", "History", "Science"],
        "description": "From a renowned historian comes a groundbreaking narrative of humanity’s creation and evolution—a #1 international bestseller—that explores the ways in which biology and history have defined us and enhanced our understanding of what it means to be 'human'."
    },

    # Genre Fillers (20-29)
    {
        "id": "fb21",
        "title": "Dune",
        "authors": ["Frank Herbert"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780441172719-M.jpg",
        "publishedDate": "1965",
        "isbn": "9780441172719",
        "publisher": "Ace Books",
        "pageCount": 896,
        "categories": ["Science Fiction", "Classics", "Fantasy"],
        "description": "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world where the only thing of value is the 'spice' melange, a drug capable of extending life and enhancing consciousness."
    },
    {
        "id": "fb22",
        "title": "The Hobbit",
        "authors": ["J.R.R. Tolkien"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780547928227-M.jpg",
        "publishedDate": "1937",
        "isbn": "9780547928227",
        "publisher": "Mariner Books",
        "pageCount": 300,
        "categories": ["Fantasy", "Classics", "Fiction"],
        "description": "Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, rarely traveling further than his pantry or cellar. But his contentment is disturbed when the wizard Gandalf and a company of thirteen dwarves arrive on his doorstep one day to whisk him away on an unexpected journey."
    },
    {
        "id": "fb23",
        "title": "Ender's Game",
        "authors": ["Orson Scott Card"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780812550702-M.jpg",
        "publishedDate": "1985",
        "isbn": "9780812550702",
        "publisher": "Tor Science Fiction",
        "pageCount": 324,
        "categories": ["Science Fiction", "Classics", "Young Adult"],
        "description": "Andrew 'Ender' Wiggin thinks he is playing computer simulated war games; he is, in fact, engaged in something far more desperate. The result of genetic experimentation, Ender may be the military genius Earth desperately needs in a war against an alien enemy seeking to destroy all human life."
    },
    {
        "id": "fb24",
        "title": "Dark Matter",
        "authors": ["Blake Crouch"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781101904220-M.jpg",
        "publishedDate": "2016",
        "isbn": "9781101904220",
        "publisher": "Crown",
        "pageCount": 342,
        "categories": ["Science Fiction", "Thriller", "Mystery"],
        "description": "Jason Dessen is walking home through the chilly Chicago streets one night, looking forward to a quiet evening in front of the fireplace with his wife, Daniela, and their son, Charlie—when his reality shatters. 'Are you happy in your life?' Those are the last words Jason Dessen hears before the masked abductor knocks him unconscious."
    },
    {
        "id": "fb25",
        "title": "The Martian",
        "authors": ["Andy Weir"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780553418026-M.jpg",
        "publishedDate": "2011",
        "isbn": "9780553418026",
        "publisher": "Crown",
        "pageCount": 369,
        "categories": ["Science Fiction", "Fiction", "Adventure"],
        "description": "Six days ago, astronaut Mark Watney became one of the first people to walk on Mars. Now, he's sure he'll be the first person to die there. After a dust storm nearly kills him and forces his crew to evacuate while thinking him dead, Mark finds himself stranded and completely alone with no way to even signal Earth that he’s alive."
    },
    {
        "id": "fb26",
        "title": "Gone Girl",
        "authors": ["Gillian Flynn"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780307588371-M.jpg",
        "publishedDate": "2012",
        "isbn": "9780307588371",
        "publisher": "Crown",
        "pageCount": 419,
        "categories": ["Thriller", "Mystery", "Fiction"],
        "description": "On a warm summer morning in North Carthage, Missouri, it is Nick and Amy Dunne’s fifth wedding anniversary. Presents are being wrapped and reservations are being made when Nick’s clever and beautiful wife disappears from their rented McMansion on the Mississippi River."
    },
    {
        "id": "fb27",
        "title": "The Silent Patient",
        "authors": ["Alex Michaelides"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9781250301697-M.jpg",
        "publishedDate": "2019",
        "isbn": "9781250301697",
        "publisher": "Celadon Books",
        "pageCount": 336,
        "categories": ["Thriller", "Mystery", "Psychological Thriller"],
        "description": "Alicia Berenson’s life is seemingly perfect. A famous painter married to an in-demand fashion photographer, she lives in a grand house with big windows overlooking a park in one of London’s most desirable areas. One evening her husband Gabriel returns home late from a fashion shoot, and Alicia shoots him five times in the face, and then never speaks another word."
    },
    {
        "id": "fb28",
        "title": "The Da Vinci Code",
        "authors": ["Dan Brown"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780307474278-M.jpg",
        "publishedDate": "2003",
        "isbn": "9780307474278",
        "publisher": "Anchor",
        "pageCount": 489,
        "categories": ["Thriller", "Mystery", "Fiction"],
        "description": "While in Paris, Harvard symbologist Robert Langdon is awakened by a phone call in the dead of the night. The elderly curator of the Louvre has been murdered inside the museum, his body covered in baffling symbols. As Langdon and gifted French cryptologist Sophie Neveu sort through the bizarre riddles, they are stunned to discover a trail of clues hidden in the works of Leonardo da Vinci."
    },
    {
        "id": "fb29",
        "title": "The Girl with the Dragon Tattoo",
        "authors": ["Stieg Larsson"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780307269751-M.jpg",
        "publishedDate": "2005",
        "isbn": "9780307269751",
        "publisher": "Knopf",
        "pageCount": 480,
        "categories": ["Thriller", "Mystery", "Crime"],
        "description": "Harriet Vanger, a scion of one of Sweden's wealthiest families disappeared over forty years ago. All these years later, her aged uncle continues to seek the truth. He hires Mikael Blomkvist, a crusading journalist recently trapped by a libel conviction, to investigate. He is aided by the pierced and tattooed punk prodigy Lisbeth Salander."
    },
    {
        "id": "fb30",
        "title": "Big Little Lies",
        "authors": ["Liane Moriarty"],
        "thumbnail": "https://covers.openlibrary.org/b/isbn/9780399167065-M.jpg",
        "publishedDate": "2014",
        "isbn": "9780399167065",
        "publisher": "G.P. Putnam's Sons",
        "pageCount": 460,
        "categories": ["Fiction", "Mystery", "Chick Lit"],
        "description": "Madeline is a force to be reckoned with. She’s funny, biting, and passionate; she remembers everything and forgives no one. Celeste is the kind of beautiful woman who makes the world stop and stare but is paying a price for the illusion of perfection. New to town, single mom Jane is so young that another mother mistakes her for a nanny. These three women are at different crossroads, but they will all wind up in the same shocking place."
    },

    # Magazines (30-32)
    {
        "id": "fb31",
        "title": "The New Yorker",
        "authors": ["David Remnick"],
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/The_New_Yorker.svg/1200px-The_New_Yorker.svg.png",
        "publishedDate": "Weekly",
        "isbn": "N/A",
        "publisher": "Condé Nast",
        "pageCount": 80,
        "categories": ["Magazine", "News", "Culture"],
        "description": "The New Yorker is an American weekly magazine featuring journalism, commentary, criticism, essays, fiction, satire, cartoons, and poetry. Starting as a weekly in 1925, the magazine is now published 47 times annually, with five of these issues covering two-week spans."
    },
    {
        "id": "fb32",
        "title": "The Economist",
        "authors": ["The Economist Group"],
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/6/6c/The_Economist_Logo.svg",
        "publishedDate": "Weekly",
        "isbn": "N/A",
        "publisher": "The Economist Group",
        "pageCount": 90,
        "categories": ["Magazine", "News", "Economics"],
        "description": "The Economist is an international weekly newspaper printed in magazine-format and published digitally that focuses on current affairs, international business, politics, and technology."
    },
    {
        "id": "fb33",
        "title": "TIME Magazine",
        "authors": ["Time USA"],
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Time_Magazine_logo.svg/2560px-Time_Magazine_logo.svg.png",
        "publishedDate": "Weekly",
        "isbn": "N/A",
        "publisher": "Time USA, LLC",
        "pageCount": 60,
        "categories": ["Magazine", "News", "Current Events"],
        "description": "Time is an American news magazine and news website published and based in New York City. For nearly a century, it was published weekly, but by March 2020 it had switched to a bi-weekly schedule."
    }
]


def _normalize(item):
    """
    Normalize Google Books API response into a standardized book dictionary.

    Extracts and formats book information from the API's nested structure,
    handles missing fields with defaults, and ensures HTTPS for thumbnails.

    Args:
        item (dict): Raw book item from Google Books API response

    Returns:
        dict: Normalized book dictionary with standard fields
    """
    v = item.get("volumeInfo", {}) or {}
    il = v.get("imageLinks", {}) or {}

    # Get thumbnail, fallback to placeholder if missing
    thumbnail = il.get("thumbnail", "") or il.get("smallThumbnail", "")
    if not thumbnail:
        thumbnail = "https://via.placeholder.com/128x196?text=No+Cover"
    if thumbnail.startswith("http://"):
        thumbnail = thumbnail.replace("http://", "https://")

    # Extract ISBN, prefer ISBN-13 over ISBN-10
    isbn = "N/A"
    identifiers = v.get("industryIdentifiers", [])
    for ident in identifiers:
        if ident.get("type") == "ISBN_13":
            isbn = ident.get("identifier")
            break
        elif ident.get("type") == "ISBN_10":
            isbn = ident.get("identifier")

    return {
        "id": item.get("id", ""),
        "title": v.get("title", "Unknown Title"),
        "authors": v.get("authors", []) or ["Unknown Author"],
        "publisher": v.get("publisher", ""),
        "publishedDate": v.get("publishedDate", ""),
        "description": v.get("description", "No description available."),
        "categories": v.get("categories", []) or [],
        "thumbnail": thumbnail,
        "infoLink": v.get("infoLink", ""),
        "language": v.get("language", "en") or "en",
        "averageRating": v.get("averageRating", None),
        "pageCount": v.get("pageCount", 0),
        "isbn": isbn
    }


def search_books(query: str, max_results=10, page=1) -> list[dict]:
    """
    Search for books using the Google Books API with caching.

    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 10)
        page (int): Page number for pagination (default: 1)

    Returns:
        list[dict]: List of normalized book dictionaries, empty list if no results
    """
    if not query: return []
    start_index = (page - 1) * max_results

    # Calculate pagination offset
    cache_key = f"search:{query}:{max_results}:{page}"
    cached_data = get_from_cache(cache_key)
    if cached_data:
        print(f"Cache hit for: {query}")
        return cached_data

    # Build API request parameters
    params = {
        "q": query,
        "maxResults": max_results,
        "startIndex": start_index,
        "projection": "full",
        "langRestrict": "en"
    }
    key = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    if key: params["key"] = key

    try:
        # Make API request
        response = requests.get("https://www.googleapis.com/books/v1/volumes?", params=params, timeout=10)
        data = response.json()
        items = data.get("items", []) or []
        books = [_normalize(i) for i in items] # Normalize all book items

        # Cache successful results
        if books:
            save_to_cache(cache_key, books)
            return books
        return []
    except Exception as e:
        print("Error fetching books:", e)
        return []


def get_daily_book():
    """
    Get a daily featured book selection.

    Uses a deterministic seed based on today's date to select
    a consistent book for the entire day.

    Returns:
        dict: A single book dictionary from the search results or fallback
    """

    # Simple daily recommendation logic based on FALLBACK_BOOKS
    # Import complete list to ensure fallback works
    from .app import FALLBACK_BOOKS as FB
    # Search for seasonal/holiday books
    search_pool_query = "subject:christmas OR title:Holiday"
    candidates = search_books(search_pool_query, max_results=10)
    if not candidates: candidates = FB

    # Use today's date as seed for consistent daily selection
    today = datetime.date.today()
    seed = today.toordinal()
    return candidates[seed % len(candidates)]


def get_you_might_like():
    """
    Generate personalized book recommendations.

    Randomly selects a topic and returns a sample of books from that category.

    Returns:
        list[dict]: List of 4 recommended book dictionaries
    """
    from .app import FALLBACK_BOOKS as FB

    # Define interesting topics to choose from
    topics = ["subject:thriller", "subject:romance", "subject:history", "subject:biography"]
    selected_topic = random.choice(topics)

    # Search for books in the selected topic
    books = search_books(f"{selected_topic}", max_results=10)
    if not books: return random.sample(FB, min(4, len(FB)))
    return random.sample(books, min(4, len(books)))


# Deduplication & Disambiguation Logic

def is_text_about_author(text, author_name=None):
    """
    Validate if retrieved text is actually about the specified author.

    This prevents disambiguation issues like "Karel Smejkal" returning
    "Czech Informel" (an art movement) instead of the author's biography.

    Uses a multi-layered validation approach:
    1. Blocklist: Rejects generic descriptions of movements/objects/places
    2. Name matching: Ensures author's name appears early in the text
    3. Keyword whitelist: Confirms presence of author-related terms

    Args:
        text (str): The text to validate
        author_name (str, optional): The author's name to check for

    Returns:
        bool: True if text is about the author, False otherwise
    """

    if not text:
        return False

    text_lower = text.lower()

    # 1. Blocklist mechanism: Reject descriptions of movements, objects, places
    # Example: "is described as a current..." would match the blocklist

    blocklist = [
        'is described as', 'is a movement', 'is a genre', 'is a style',
        'is a type of', 'chemical element', 'is a city', 'refers to',
        'is a term'
    ]
    if any(b in text_lower for b in blocklist):
        return False

    # 2. Name checking mechanism: Author's name should appear early in text
    # Example: "Karel Smejkal" won't appear in "Czech Informel is described as..."
    if author_name:
        # Split name into words (e.g., "Jojo Moyes" -> ["jojo", "moyes"])
        name_parts = author_name.lower().split()
        # Check if surname or first name appears in opening text
        # Allow for "Moyes was born..." or "Jojo is..."
        # Extended to first 250 characters for flexibility
        intro_text = text_lower[:250]
        name_found = any(part in intro_text for part in name_parts if len(part) > 2)

        if not name_found:
            # If name is completely absent from the opening, likely wrong result
            return False

    # 3. Keyword whitelist (keep original logic as auxiliary check)
    keywords = [
        'author', 'writer', 'novelist', 'poet', 'journalist',
        'historian', 'philosopher', 'biographer', 'essayist',
        'playwright', 'screenwriter', 'editor', 'literature',
        'fiction', 'books', 'published', 'wrote', 'born', 'died'
    ]

    return any(k in text_lower for k in keywords)


def _get_author_from_open_library(author_name):
    """
    Fetch author information from Open Library API.

    Args:
        author_name (str): Name of the author to search for

    Returns:
        dict: Author information including bio, image, and birth date, or None if not found
    """
    try:
        # Search for author
        search_url = "https://openlibrary.org/search/authors.json"
        params = {"q": author_name}
        headers = {'User-Agent': 'BookFinderApp/1.0'}
        resp = requests.get(search_url, params=params, headers=headers, timeout=5)
        data = resp.json()

        if data.get('numFound', 0) > 0:
            # Get the top match
            top_hit = data['docs'][0]
            author_key = top_hit.get('key')
            details_url = f"https://openlibrary.org/authors/{author_key}.json" # Fetch detailed author information
            details_resp = requests.get(details_url, headers=headers, timeout=5)
            details = details_resp.json()

            bio = details.get('bio', '')
            if isinstance(bio, dict): bio = bio.get('value', '')
            born = details.get('birth_date', 'N/A')

            # Build image URL if available
            image = None
            if details.get('photos'):
                photo_id = details['photos'][0]
                image = f"https://covers.openlibrary.org/b/id/{photo_id}-L.jpg"

            return {"bio": bio, "image": image, "born": born, "source": "OpenLibrary"}
    except Exception as e:
        print(f"OpenLibrary Error: {e}")
    return None


def get_author_info(author_name):
    """
    Fetch comprehensive author information from multiple sources.

    Uses a multi-strategy approach with validation:
    1. Direct Wikipedia lookup (exact page match)
    2. Fuzzy Wikipedia search (handles name variations)
    3. Open Library API fallback

    Each strategy includes validation to prevent disambiguation errors
    (e.g., returning "Czech Informel" when searching for "Karel Smejkal").

    Args:
        author_name (str): Name of the author to search for

    Returns:
        dict: Author information with bio, image, birth date, and source,
              or None if no valid information found
    """
    if not author_name: return None
    result = {"bio": None, "image": None, "born": "N/A", "source": None}

    #1: Direct Wiki lookup
    print(f"Strategy 1: Direct Wiki lookup for {author_name}...")
    try:
        formatted_name = author_name.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_name}"
        headers = {'User-Agent': 'BookFinderApp/1.0'}
        resp = requests.get(url, headers=headers, timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            bio = data.get('extract', '')
            # Pass author_name for strong validation
            if is_text_about_author(bio, author_name):
                result['bio'] = bio
                if 'thumbnail' in data:
                    result['image'] = data['thumbnail'].get('source')
                elif 'originalimage' in data:
                    result['image'] = data['originalimage'].get('source')
                result['source'] = "Wikipedia (Direct)"
                print("-> Success (Direct)")
                return result
            else:
                print(f"-> Validation Failed: Text not about {author_name}")
    except Exception as e:
        print(f"Direct Wiki Error: {e}")

    # 2: Fuzzy Wikipedia search
    if not result['bio']:
        print(f"Strategy 2: Fuzzy Wiki search for {author_name}...")
        try:
            search_query = f"{author_name} author"
            search_results = wikipedia.search(search_query)
            if search_results:
                wiki_page = wikipedia.page(search_results[0], auto_suggest=False)
                # Pass author_name for strong validation
                if is_text_about_author(wiki_page.summary, author_name):
                    result['bio'] = wiki_page.summary.split('\n')[0]
                    if wiki_page.images: result['image'] = wiki_page.images[0]
                    result['source'] = "Wikipedia (Fuzzy)"
                    print("-> Success (Fuzzy)")
                    return result
        except Exception as e:
            print(f"Wiki Search Error: {e}")

    # 3: Open Library fallback
    if not result['bio']:
        print(f"Strategy 3: Trying Open Library for {author_name}...")
        ol_data = _get_author_from_open_library(author_name)
        if ol_data and ol_data.get('bio'):
            result.update(ol_data)
            print("-> Success (Open Library)")
            return result

    return None


def get_book_by_id(book_id):
    """
    Retrieve detailed book information by ID.

    Checks fallback books first (IDs starting with 'fb'), then queries
    the Google Books API. Also fetches author information if available.

    Args:
        book_id (str): Unique book identifier

    Returns:
        dict: Complete book dictionary with author info, or None if not found
    """
    book = None
    # Import FALLBACK_BOOKS from app.py to avoid circular imports
    # In production, consider moving FALLBACK_BOOKS to a separate data.py file
    from .app import FALLBACK_BOOKS as FB

    # Check fallback books first (offline data)
    if book_id.startswith('fb'):
        for b in FB:
            if b['id'] == book_id:
                book = b.copy()
                break

    # Query Google Books API if not found in fallback
    if not book:
        url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                book = _normalize(data)
        except Exception:
            pass

    # Enrich with author information if book found
    if book and book.get('authors'):
        primary_author = book['authors'][0]
        auth_info = get_author_info(primary_author)
        if auth_info:
            if auth_info.get('bio'): book['author_bio'] = auth_info['bio']
            if auth_info.get('image'): book['author_image'] = auth_info['image']

    return book