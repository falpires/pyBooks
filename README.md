# Project 1

Web Programming with Python and JavaScript


## Getting started

- Set the environment variables API_KEY and DATABASE_URL to your goodreads API Key and your SQLAlchemy DB URI
- Set the FLASK_APP environment variable to "application.py"
- Run "pip install -r requirements.txt" from your python or some virtual environment
- Run "flask run" from the "application.py" folder


## To create a virtual environment for this project

- Run "python -m venv .env"
- Run the "activate" script. It is under "./env/scripts" and is named "activate". The bat one is for windows CMD, the ps1 is for Powershell, and the one without extension is for linux bash/shell.




## TO DO

- [x] Registration
- [x] Login
- [x] Logout
- [x] Import
- [x] Search (ISBN, Title or Author)
- [x] Book page (Page with details of the book, showing Title, Author, Year, ISBN Number, and reviews from my DB)
- [x] Goodreads Review Data (Should show on the book page, average review and number of reviews)
- [x] Review Submission (1 to 5 rating, and text about the rating) Only one per user/book
- [x] API for route(/api/<string:isbn>) should show json containing: {"title", "author", "year", "isbn", "review_count", "average_score"}
- [ ] Style it all! CSS!