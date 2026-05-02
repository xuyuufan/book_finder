# 📚 BookFinder

## Project Overview

**BookFinder** is a web application designed to enhance the book discovery experience by combining a powerful **Smart Book Search** function with personalized, **Content-Based Book Recommendations**.

This project is developed using **Flask** and leverages an external **Google Books API** for comprehensive book data.

### Key Features

**Smart Search**: Allows users to search for books by various criteria, including title, author, publisher, ISBN, or keywords.
**Structured Results**: Search results are displayed in a clear, structured manner, complete with detailed book information like summaries and publication dates.
**Content-Based Recommendations**: Implements recommendation algorithms (e.g., using a book's attributes) to suggest relevant books, displayed on the homepage and search results pages.

---

## 🛠️ Local Setup and Installation

Follow these steps to set up the project environment on your local machine.

### 1. Prerequisites (Install Git)

Ensure you have Git installed. If not, download it from the official website.

Verify installation:

```bash
git --version 
```

### 2. User Configuration

[cite_start]Set your global Git username and email using the information provided on Brightspace[cite: 13]:

```bash
git config --global user.name " Your Name "
git config --global user.email " Your School Email "
```

### 3. Clone the Project Skeleton

Clone the repository to your local machine:

```bash
git clone [https://git.liacs.nl/group2/bookfinder.git]
```

### 4. Setup Virtual Environment and Dependencies

| Step | Command (Mac/Linux) | Command (Windows PowerShell) | Purpose |
| :--- | :--- | :--- | :--- |
| **Enter Dir** | `cd bookfinder` | `cd bookfinder` | Switch to the project root folder. |
| **Create/Activate** | `python3 -m venv .venv` <br> `source .venv/bin/activate` | `python -m venv .venv` <br> `.venv\Scripts\activate` | Ensures all operations are within an isolated environment. The terminal should start with `(.venv)`. |
| **Install Deps** | `pip install -r requirements.txt` | `pip install -r requirements.txt` | Installs required libraries (Flask, requests, scikit-learn, etc.). |

### 5. API Key Configuration

Copy the example environment file and rename it to `.env`:

**Mac/Linux**: `cp .env.example .env` 
**Windows**: `copy .env.example .env` 

You **must** configure the following variables in your `.env` file:

`GOOGLE_BOOKS_API_KEY`: The external API key required for data retrieval.
`SECRET_KEY`: A secret key for Flask application security.

### 6. Create Your Feature Branch
Create your designated feature branch and switch to it. PLEASE NOTE：Never work directly on the main branch.

| Role | Branch Name Example | Command |
| :--- | :--- | :--- |
| **A** (Backend Core) | `feat/backend-core` | `git checkout -b feat/backend-core` |
| **B** (External Data) | `feat/books-api` | `git checkout -b feat/books-api` |
| **C** (Recommendation) | `feat/reco-tfidf-genre` | `git checkout -b feat/reco-tfidf-genre` |
| **D** (Frontend UI) | `feat/frontend-ui` | `git checkout -b feat/frontend-ui` |
| **E** (Deployment/Ops) | `ops/deploy` | `git checkout -b ops/deploy` |
| **F** (Documentation) | `docs/readme` | `git checkout -b docs/readme` |

## Project Structure

| File/Folder | Responsibility | Purpose |
| :--- | :--- | :--- |
| `app/` | A, B, C | Contains all Python backend logic (Flask routes, API integration, algorithms). |
| `app/app.py` | A (Backend Core) | Project entry point, contains Flask startup and `@app.route` definitions. |
| `app/books.py` | B (External Data) | Encapsulates Google Books API calls and data cleaning/standardization logic. |
| `app/recommend.py` | C (Recommendation) | Implements TF-IDF and Genre recommendation algorithms. |
| `templates/` | D (Frontend UI) | Stores all HTML web pages (e.g., `base.html`, `index.html`, `results.html`). |
| `static/` | D (Frontend UI) | Stores static resources, primarily `styles.css` for all page styling. |
| `.env.example` | F (Documentation) | Template for required environment variables. |
| `requirements.txt` | E (Deployment) | Lists all necessary Python libraries for the project. |
| `Procfile` | E (Deployment) | Instructions for the deployment platform (e.g., Heroku) on how to start the Flask application. |
| `README.md` | F (Documentation) | Project documentation, setup, and key details. | 

##  Daily Standardized Git Workflow

### Before Coding (Daily Start)

| Step | Git Command / Operation | Purpose |
| :--- | :--- | :--- |
| **1. Activate Environment** | `source .venv/bin/activate` | Ensure all work is done in the isolated virtual environment. |
| **2. Switch to Branch** | `git checkout [Your Branch Name]` | Ensure you are on your feature branch to avoid contaminating `main`. |
| **3. Pull Latest Code** | `git pull origin main` | Download the latest stable code from the `main` branch to avoid merge conflicts later. |

### After Coding (Daily End)

| Step | Git Command / Operation (Example) | Purpose |
| :--- | :--- | :--- |
| **1. Add Changes** | `git add .` | Add all modified files to the staging area. |
| **2. Commit Message** | `git commit -m "feat: complete standardized books API and data structure"` | Use the **Conventional Commits** format: `[type]: [space] [short description]`. |
| **3. Push Branch** | `git push origin [Your Branch Name]` | Push your local feature branch and all new commits to the remote GitLab repository. |