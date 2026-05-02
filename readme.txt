=============================================================================
PROJECT: BookFinder
=============================================================================

[1] PROJECT OVERVIEW
-----------------------------------------------------------------------------
BookFinder is a web application designed to enhance the book discovery
experience by combining a powerful Smart Book Search function with
personalized, Content-Based Book Recommendations.

Key Features:
- Smart Search: Search by title, author, publisher, ISBN, or keywords.
- Structured Results: Clear display with summaries and publication dates.
- Content-Based Recommendations: Algorithms suggest relevant books based on
  attributes.

-----------------------------------------------------------------------------
[2] SETUP AND INSTALLATION
-----------------------------------------------------------------------------
Follow these steps to set up and run the project.

1. PREREQUISITES
   Ensure you have Python 3.x and Git installed.

2. CLONE THE REPOSITORY
   Open your terminal/command prompt and run:
   git clone https://git.liacs.nl/group2/bookfinder.git

3. SETUP VIRTUAL ENVIRONMENT
   It is recommended to use a virtual environment.

   - Mac/Linux:
     python3 -m venv .venv
     source .venv/bin/activate

   - Windows:
     python -m venv .venv
     .venv\Scripts\activate

4. INSTALL DEPENDENCIES
   This ensures all required libraries (Flask, requests, etc.) are installed.
   Run:
   pip install -r requirements.txt

5. API CONFIGURATION
   Create a file named '.env' in the root directory.
   Add your API keys inside it (format: KEY_NAME=your_key_here):
   - GOOGLE_BOOKS_API_KEY
   - SECRET_KEY

-----------------------------------------------------------------------------
[3] HOW TO EXECUTE THE CODE
-----------------------------------------------------------------------------
Once the installation is complete:

1. Start the application by running:
   python main.py

2. Open your web browser and navigate to:
   http://127.0.0.1:5000/

-----------------------------------------------------------------------------
[4] FILE STRUCTURE & EXPLANATION
-----------------------------------------------------------------------------
- main.py: The entry point to run the Flask application.
- app/: Contains the application logic (routes, models, views).
  - books.py: Handles Google Books API integration.
  - recommend.py: Contains recommendation algorithms.
- templates/: Contains HTML files (index.html, results.html, etc.).
- static/: Contains CSS stylesheets and images.
- requirements.txt: List of python dependencies.