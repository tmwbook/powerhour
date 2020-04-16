from api_utils import _get, _post, api_call, API_BASE


@api_call
def get_playlists():
    return _get(API_BASE+'/me/playlists')