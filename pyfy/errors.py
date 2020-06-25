class SpotifyAPIError(Exception):

    def __init__(self, status, message, reason, usr_message=""):
        if usr_message == "":
            usr_message = f"{status} {reason}: {message}"
        super().__init__(usr_message)
        self.status = status
        self.message = message
        self.reason = reason


class SingletonViolation(Exception):
    pass
