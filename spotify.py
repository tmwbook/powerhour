from api_utils import API_BASE, _get, _post, api_call


@api_call
def get_playlists():
    return _get(API_BASE+'/me/playlists')


@api_call
def queue_song(spotify_uri: str):
    """queue given song, returns current player status"""
    _post(API_BASE+"/me/player/queue", data={"uri": spotify_uri})
    return _get(API_BASE+"/me/player")

@api_call
def get_playlist(playlist_id: str):
    return _get(f'{API_BASE}/playlists/{playlist_id}')


def queue_playlist(playlist_id: str):
    """queue all songs in a playlist"""
    # TODO(Tom): Stress test this, no idea when this will get rate limited
    r = get_playlist(playlist_id)
    songs = []
    current_page = r.json()['tracks']
    while current_page:
        for track in current_page['items']:
            songs.append(track['track']['uri'])
        current_page = current_page['next']
    for song in songs:
        queue_song(song)
