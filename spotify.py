from api_utils import API_BASE, _get, _post, api_call


@api_call
def get_playlists():
    return _get(API_BASE+'/me/playlists')


@api_call
def queue_song(spotify_uri: str):
    """queue given song, returns current player status"""
    _post(API_BASE+"/me/player/queue", data={"uri": spotify_uri})
    return _get(API_BASE+"/me/player")
