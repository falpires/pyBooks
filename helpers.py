from functools import wraps
from flask import request, redirect, url_for, session
import requests


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def goodreads(api_key, isbn):
    """
    Calls the goodreads API for getting review data

    Arguments:
        api_key {string} -- [API Key for goodreads API]
        isbn {string} -- [ISBN for the book query]
    """

    response = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key": api_key, "isbns": isbn})

    return response.json()
    
