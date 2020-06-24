from flask import redirect, url_for
from flask_login import current_user, logout_user

from db import db


def query_active_token():
    return current_user.access_token


def query_refresh_token():
    return current_user.refresh_token


def store_refreshed_token(new_tkn):
    current_user.access_token = new_tkn
    db.session.commit()


def failed_api_call():
    """Callback for token manager if api fails
    to auth twice"""
    logout_user()
    return redirect('/')
