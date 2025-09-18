from hashlib import md5

from .exceptions import NeedsAPIKey, NoTokenProvided


def get_item_hash(item_name: str) -> str:
    return md5(item_name.encode()).hexdigest()


def needs_token(func):
    def wrapper(self, *args, **kwargs):
        if not self._token:
            raise NoTokenProvided("Set a token to use this method")

        return func(self, *args, **kwargs)

    return wrapper


def needs_api_key(func):
    def wrapper(self, *args, **kwargs):
        if not self._api_key:
            raise NeedsAPIKey("Set an API key to use this method")

        return func(self, *args, **kwargs)

    return wrapper
