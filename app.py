from urllib.parse import urlencode

from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, login_required, login_user, current_user
from requests import get, post

from env import APP_SECRET, CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, SCOPES
from db import db, User
from api_utils import API_BASE, TOKEN_ENDPOINT, OAUTH_ENDPOINT, _refresh_tokens
import spotify

app = Flask(__name__)
app.secret_key = APP_SECRET

login_manager = LoginManager()
login_manager.init_app(app)

# This is a hack, but I am only using 1 app, so it is safe to do
# Essentually manually doing what SQLAlchemy(app) would do
db.app = app
db.init_app(app)

db.create_all()


###############################
### Spotify API Auth helpers
###############################

def get_auth_url(perms=[], scopes=[]):
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URL,
    }
    if scopes:
        params['scope'] = " ".join(scope for scope in scopes)
    return OAUTH_ENDPOINT+"?"+urlencode(params)


def get_tokens(code):
    """Gets the refresh and access tokens from spotify"""
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = post(TOKEN_ENDPOINT, data=params)
    if r.status_code is 200:
        # We should now have a response with the tokens
        return r.json()
    # If we get here then we have failed
    return redirect(url_for('/'))


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@app.route('/login/result')
def auth_result():
    if request.args.get('code', None):
        # Continue the authentication process
        tokens = get_tokens(request.args.get('code'))
        r = get(API_BASE+'/me', headers={"Authorization": "Bearer "+tokens["access_token"]}).json()
        local_user = User.query.filter_by(spotify_id=r['id']).first()
        if local_user:
            local_user.access_token = ['access_token']
            local_user.refresh_token = ['refresh_token']
        else:
            local_user = User(
                spotify_id = r['id'],
                access_token = tokens['access_token'],
                refresh_token = tokens['refresh_token'],
            )
            db.session.add(local_user)
        db.session.commit()
        login_user(local_user)
        return redirect(url_for('hello'))
    else:
        return redirect(url_for('/'))


###############################
### Routes
###############################
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('hello'))
    context = {
        "spotify_auth_url": get_auth_url(SCOPES),
    }
    return render_template('index.html', **context)


@app.route('/hello')
@login_required
def hello():
    return render_template('result.html', data=current_user.__dict__)


@app.route('/playlists')
@login_required
def get_playlists():
    r = spotify.get_playlists()
    return render_template('result.html', data=r.json())
