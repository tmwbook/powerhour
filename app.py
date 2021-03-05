import heapq
from datetime import datetime, timedelta
from threading import Thread, Timer
from time import sleep
from urllib.parse import urlencode

from flask import Flask, redirect, render_template, request, url_for, wrappers
from flask_login import LoginManager, current_user, login_required, login_user
from pyfy.api_utils import (API_BASE, OAUTH_ENDPOINT, TOKEN_ENDPOINT,
                            TokenManager)
from pyfy.wrappers import player, playlists
from requests import get, post

from db import PlaylistRequest, User, db
from env import APP_SECRET, CLIENT_ID, CLIENT_SECRET, DEV, SCOPES
from web_utils import (failed_api_call, query_active_token,
                       query_refresh_token, scheduled_events,
                       store_refreshed_token)

app = Flask(__name__, static_folder="powerhour-fe/build/")

if DEV:
    from flask_cors import CORS
    CORS(app)

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

def consierge_thread():
    while True:
        if len(scheduled_events) == 0:
            sleep(5)
        elif (req := scheduled_events[0][1]).time < datetime.now():
            player.start_playback(context_uri=req.playlist_id)
            heapq.heappop(scheduled_events)

Thread(target=consierge_thread).start()

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
    return redirect(url_for('index'))


###############################
### Routes
###############################
@app.route('/')
def index():
    if DEV:
        return redirect("http://localhost:3001")
    if current_user.is_authenticated:
        return redirect(url_for('hello'))
    context = {
        "spotify_auth_url": TokenManager.get_instance().gen_auth_url(
            "http://localhost:3000/login/result",
            SCOPES,
            True
        ),
    }
    return app.send_static_file('index.html')


@app.route('/hello')
@login_required
def hello():
    return {"data": repr(current_user.__dict__)}, 200


@app.route('/playlists')
@login_required
def get_playlists():
    r = playlists.get_playlists()
    return r.json(), 200


@app.route('/test')
@login_required
def play_music():
    # spotify:track:2QyuXBcV1LJ2rq01KhreMF ON - BTS
    r = player.start_playback(track_uris=["spotify:track:2QyuXBcV1LJ2rq01KhreMF"])
    return redirect(url_for('hello'))


@app.route('/test_playlist', methods=['POST'])
@login_required
def play_playlist():
    if request.method == "POST":
        if (data := request.get_json()) is None:
            return {"error": "expected JSON"}, 200
        r = player.start_playback(context_uri=data.get("playlist_id"))
        return "", 200
    # spotify:playlist:39LyZo1T7CceLqQxujIcEx Bang Bang
    player.start_playback(context_uri="spotify:playlist:39LyZo1T7CceLqQxujIcEx")
    return redirect(url_for('hello'))

@app.route('/schedule_playlist', methods=["POST"])
@login_required
def schedule_playback():
    if (data := request.get_json()) is None:
        return {"error": "expected JSON"}, 200
    hrs, mins = data.get("time").split(":")
    tz_diff = data.get("offset") - (5*60)
    scheduled = datetime.now().replace(hour=int(hrs), minute=int(mins), second=0, microsecond=0)
    scheduled += timedelta(minutes=tz_diff)
    req = PlaylistRequest(user_id=current_user.id, playlist_id=data.get("playlist_id"), time=scheduled)
    heapq.heappush(scheduled_events, (scheduled, req))
    db.session.add(req)
    db.session.commit()
    return "", 200

@app.route('/test_album')
def play_album():
    # spotify:album:6Yi4tnW7O7FUW9kK3bAUhT Play with Fire - The Reign of Kindo
    player.start_playback(context_uri="spotify:album:6Yi4tnW7O7FUW9kK3bAUhT")
    return redirect(url_for('hello'))

@app.route('/check_auth')
@login_required
def check_auth():
    return "", 200

@app.route('/get_auth_url')
def get_auth_url():
    return {"url": TokenManager.get_instance().gen_auth_url("http://localhost:3000/login/result", SCOPES)}
