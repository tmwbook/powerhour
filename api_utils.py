from requests import get, post, put

from spotify_execptions import SingletonViolation, SpotifyAPIError

API_BASE = "https://api.spotify.com/v1"

TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
OAUTH_ENDPOINT = "https://accounts.spotify.com/authorize"


class TokenManager():
    """Singleton class to interact with the Spotify token API
    (Method 1 of authentication) for existing tokens. First time
    authentications and expired refresh tokens requiring reauthentication
    against Spotify's IdP are not handled by this class.
    
        client_id: A string of your application's client_id from Spotify

        client_secret: A string of your application's client_secret from Spotify

        token_query_source: A function that will return what the current
            user's token is.

            This would be useful in a web application where there could be
            multiple active user sessions. For example:
            def token_query_source():
                return db.query(current_user).token

        refresh_token_query_source: A function that will return what the
            current user's refresh token is.

            This would be the same as `token_query_source` but for refresh
            tokens.

        store_refreshed_token: A function that takes 1 argument (string)
            that will store a token for the current user if the old one
            expires. For example:
            def store_refreshed_token(new_tkn):
                user = db.query(current_user)
                user.token = newtkn
                db.commit()

        api_fail_callback: A function that you would like to be called after
            two Access Denied (or similar 400) responses. Its value will be
            returned instead of the result of the API call.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise AttributeError("TokenManager has not been initialized yet.")
        return cls._instance

    @classmethod
    def initialize(
            cls,
            client_id,
            client_secret,
            token_query_source,
            refresh_token_query_source,
            store_refreshed_token,
            api_fail_callback
    ):
        if cls._instance is None:
            cls(
                client_id,
                client_secret,
                token_query_source,
                refresh_token_query_source,
                store_refreshed_token,
                api_fail_callback
            )
        return cls._instance


    def __init__(
            self,
            client_id,
            client_secret,
            token_query_source,
            refresh_token_query_source,
            store_refreshed_token,
            api_fail_callback
    ):
        if TokenManager._instance is not None:
            raise SingletonViolation("Attepted to instantiate TokenManager when it has"
                            " already been initilized. Use get_instance() instead.")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_query_source = token_query_source
        self.refresh_token_query_source = refresh_token_query_source
        self.store_refreshed_token = store_refreshed_token
        self.api_fail_callback = api_fail_callback

        TokenManager._instance = self

    def refresh_tokens(self):
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token_query_source(),
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        r = post(TOKEN_ENDPOINT, data=params)
        if r.status_code < 400:
            self.store_refreshed_token(r.json()['access_token'])

    def get_current_token(self):
        return self.token_query_source()


def api_call(expected_error_codes):
    """
    Wrapper to take care of potential token experations
    
    expected_error_code: An iterable of codes that can be reported
        from Spotify unrelated to the token renewal.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            mngr = TokenManager.get_instance()
            # Assume the access token works:
            r = func(*args, **kwargs)
            if r.status_code in range(400, 500):
                if r.status_code in expected_error_codes:
                    raise SpotifyAPIError(
                        r.status_code,
                        r.json()['message'],
                        r.json()['reason']
                    )
                # Whoops let's try that again
                mngr.refresh_tokens()
                r = func(*args, **kwargs)
                if r.status_code in range(400, 500):
                    if r.status_code in expected_error_codes:
                        raise SpotifyAPIError(
                            r.status_code,
                            r.json()['message'],
                            r.json()['reason']
                        )
                    return mngr.api_fail_callback()
            return r
        return wrapper
    return decorator


def _get(endpoint, params=None):
    if not params:
        params = {}
    return get(
        endpoint,
        headers={
            "Authorization": "Bearer " + TokenManager.get_instance().get_current_token()
        },
        params=params
    )


def _post(endpoint, data=None):
    if not params:
        params = {}
    # Who was the spotify dev the let data in a post be in the params??????
    return post(
        endpoint,
        headers={
            "Authorization": "Bearer " + TokenManager.get_instance().get_current_token()
        },
        params=data
    )


def _put(endpoint, params=None, data=None):
    params = params or {}
    data = data or {}
    return put(
        endpoint,
        headers={
            "Authorization": "Bearer " + TokenManager.get_instance().get_current_token()
        },
        params=params,
        json=data
    )
