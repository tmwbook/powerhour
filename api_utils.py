from flask import redirect, url_for
from flask_login import current_user, logout_user
from requests import get, post, put

from db import db
from env import CLIENT_ID, CLIENT_SECRET

API_BASE = "https://api.spotify.com/v1"

TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
OAUTH_ENDPOINT = "https://accounts.spotify.com/authorize"

def _get(endpoint, params=None):
    if not params:
        params = {}
    return get(endpoint, headers={"Authorization": "Bearer "+current_user.access_token}, params=params)


def _post(endpoint, data=None):
    if not params:
        params = {}
    # Who was the spotify dev the let data in a post be in the params??????
    return post(endpoint, headers={"Authorization": "Bearer "+current_user.access_token}, params=data)


def _put(endpoint, params=None, data=None):
    params = params or {}
    data = data or {}
    return put(endpoint, headers={"Authorization": "Bearer "+current_user.access_token}, params=params, json=data)


def _refresh_tokens():
    params = {
        "grant_type": "refresh_token",
        "refresh_token": current_user.refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = post(TOKEN_ENDPOINT, data=params)
    if r.status_code < 400:
        current_user.access_token = r.json()['access_token']
        db.session.commit()


def api_call(func):
    def wrapper(*args, **kwargs):
        # Assume the access token works:
        r = func(*args, **kwargs)
        if r.status_code in range(400, 500):
            # Whoops let's try that again
            _refresh_tokens()
            r = func(*args, **kwargs)
            if r.status_code in range(400, 500):
                # Something's wrong, let's just re-auth
                logout_user()
                return redirect(url_for('index'))
        return r
    return wrapper
