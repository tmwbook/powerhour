from typing import Sequence, overload

from api_utils import API_BASE, _get, _post, _put, api_call


@api_call([])
def get_playlists():
    return _get(API_BASE+'/me/playlists')


@api_call([403, 404])
def queue_song(spotify_uri: str):
    """queue given song, returns current player status"""
    _post(API_BASE+"/me/player/queue", data={"uri": spotify_uri})
    return _get(API_BASE+"/me/player")


@api_call([403])
def get_playlist(playlist_id: str):
    return _get(f'{API_BASE}/playlists/{playlist_id}')


@api_call([403, 404])
def start_playback(device_id: str=None):
    return _put(f'{API_BASE}/me/player/play', params={"device_id": device_id})


@api_call([403, 404])
def play_track(spotify_uri: str, position_ms: int=0, device_id: str=None):
    return play_tracks([spotify_uri,], 0, position_ms, device_id)


@overload
def play_tracks(spotify_uris: Sequence[str], offset: int=0, position_ms: int=0, device_id: str=None): pass
@overload
def play_tracks(spotify_uris: Sequence[str], offset: str=None, position_ms: int=0, device_id: str=None): pass
@api_call([403, 404])
def play_tracks(spotify_uris, offset=None, position_ms=0, device_id=None):
    data = {
        "uris": spotify_uris,
        "position_ms": position_ms,
    }
    if offset:
        if isinstance(offset, int):
            data['offset'] = {'position': offset}
        else:
            data['offset'] = {'uri': offset}
    return _put(
        f'{API_BASE}/me/player/play',
        params={"device_id": device_id} if device_id else None,
        data=data
    )


@overload
def play_playlist(spotify_uri: str, offset: int=0, position_ms: int=0, device_id: str=None): pass
@overload
def play_playlist(spotify_uri: str, offset: str=None, position_ms: int=0, device_id: str=None): pass
@api_call([403, 404])
def play_playlist(spotify_uri, offset=None, position_ms=0, device_id=None):
    data = {
        "context_uri": spotify_uri,
        "position_ms": position_ms,
    }
    if offset:
        if isinstance(offset, int):
            data['offset'] = {'position': offset}
        else:
            data['offset'] = {'uri': offset}
    return _put(
        f'{API_BASE}/me/player/play',
        params={"device_id": device_id} if not device_id else None,
        data=data
    )


@overload
def play_album(spotify_uri: str, offset: int=0, position_ms: int=0, device_id: str=None): pass
@overload
def play_album(spotify_uri: str, offset: str=None, position_ms: int=0, device_id: str=None): pass
@api_call([403, 404])
def play_album(spotify_uri, offset=None, position_ms=0, device_id=None):
    return play_playlist(spotify_uri, offset, position_ms, device_id)
