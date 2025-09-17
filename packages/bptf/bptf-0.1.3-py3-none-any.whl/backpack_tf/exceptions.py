class BackpackTFException(Exception):
    pass


class NoTokenProvided(BackpackTFException):
    pass


class NeedsAPIKey(BackpackTFException):
    pass


class InvalidIntent(BackpackTFException):
    pass
