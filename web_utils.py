from flask import redirect, url_for
from flask_login import current_user, logout_user

from db import User, db

scheduled_events = []

def query_active_token():
    if (user := current_user) == None:
        user = User.query.filter_by(id=scheduled_events[0][1].user_id).first()
    return user.access_token


def query_refresh_token():
    if (user := current_user) == None:
        user = User.query.filter_by(id=scheduled_events[0][1].user_id).first()
    return user.refresh_token


def store_refreshed_token(new_tkn):
    if (user := current_user) == None:
        user = User.query.filter_by(id=scheduled_events[0][1].user_id).first()
    user.access_token = new_tkn
    db.session.commit()


def failed_api_call():
    """Callback for token manager if api fails
    to auth twice"""
    logout_user()
    return redirect('/')
