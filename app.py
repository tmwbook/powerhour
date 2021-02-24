from urllib.parse import urlencode

from flask import Flask, redirect, render_template, request, url_for, wrappers
from flask_login import LoginManager, current_user, login_required, login_user
from requests import get, post

from db import User, db
from env import APP_SECRET, CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, SCOPES
from pyfy.api_utils import (API_BASE, OAUTH_ENDPOINT, TOKEN_ENDPOINT,
                            TokenManager)
from pyfy.wrappers import player, playlists
from web_utils import (failed_api_call, query_active_token,
                       query_refresh_token, store_refreshed_token)

app = Flask(__name__)
# :///rel/path OR :////abs/path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database'
app.secret_key = APP_SECRET

login_manager = LoginManager()
login_manager.init_app(app)

# This is a hack, but I am only using 1 app, so it is safe to do
# Essentually manually doing what SQLAlchemy(app) would do
db.app = app
db.init_app(app)

db.create_all()

TokenManager.initialize(
    CLIENT_ID,
    CLIENT_SECRET,
    query_active_token,
    query_refresh_token,
    store_refreshed_token,
    failed_api_call
)

###############################
### Spotify API Auth helpers
###############################

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@app.route('/login/result')
def auth_result():
    spotify_resp = TokenManager.get_instance().handle_auth_response(request.url)
    r = get(API_BASE+'/me', headers={"Authorization": "Bearer "+spotify_resp["access_token"]}).json()
    local_user = User.query.filter_by(spotify_id=r['id']).first()
    if local_user:
        local_user.access_token = spotify_resp['access_token']
        local_user.refresh_token = spotify_resp['refresh_token']
    else:
        local_user = User(
            spotify_id = r['id'],
            access_token = spotify_resp['access_token'],
            refresh_token = spotify_resp['refresh_token'],
        )
        db.session.add(local_user)
    db.session.commit()
    login_user(local_user)
    return redirect(url_for('hello'))


###############################
### Routes
###############################
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('hello'))
    context = {
        "spotify_auth_url": TokenManager.get_instance().gen_auth_url(
            "http://localhost:3000/login/result",
            SCOPES,
            True
        ),
    }
    return render_template('index.html', **context)


@app.route('/hello')
@login_required
def hello():
    return render_template('result.html', data=current_user.__dict__)


@app.route('/playlists')
@login_required
def get_playlists():
    r = playlists.get_playlists()
    return render_template('result.html', data=r.json())


@app.route('/test')
@login_required
def play_music():
    # spotify:track:2QyuXBcV1LJ2rq01KhreMF ON - BTS
    r = player.start_playback(track_uris=["spotify:track:2QyuXBcV1LJ2rq01KhreMF"])
    return redirect(url_for('hello'))


@app.route('/test_playlist')
@login_required
def play_playlist():
    # spotify:playlist:39LyZo1T7CceLqQxujIcEx Bang Bang
    player.start_playback(context_uri="spotify:playlist:39LyZo1T7CceLqQxujIcEx")
    return redirect(url_for('hello'))


@app.route('/test_album')
def play_album():
    # spotify:album:6Yi4tnW7O7FUW9kK3bAUhT Play with Fire - The Reign of Kindo
    player.start_playback(context_uri="spotify:album:6Yi4tnW7O7FUW9kK3bAUhT")
    return redirect(url_for('hello'))
