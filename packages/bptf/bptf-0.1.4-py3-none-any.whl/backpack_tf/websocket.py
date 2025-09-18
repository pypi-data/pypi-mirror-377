import json
from typing import Any, Callable

from websockets.sync.client import connect


class BackpackTFWebsocket:
    URL = "wss://ws.backpack.tf/events"

    def __init__(
        self,
        callback: Callable[[dict | list[dict]], None],
        as_solo_entries: bool = True,
        headers: dict[str, Any] = {"batch-test": True},
        max_size: int | None = None,
        settings: dict[str, Any] = {},
    ) -> None:
        """
        Args:
            callback: Function pointer where the data to ends up
            as_solo_entries: If data to callback should be solo entries or a batched list
            headers: Additional headers to send to the socket
            settings: Additional websocket settings as a dict to be unpacked
        """
        self._callback = callback
        self._as_solo_entries = as_solo_entries
        self._headers = headers
        self._max_size = max_size
        self._settings = settings

    def _process_messages(self, data: str) -> None:
        messages = json.loads(data)

        if not self._as_solo_entries:
            self._callback(messages)
            return

        for message in messages:
            payload = message["payload"]
            self._callback(payload)

    def listen(self) -> None:
        """Listen for messages from BackpackTF"""
        with connect(
            self.URL,
            additional_headers=self._headers,
            max_size=self._max_size,
            **self._settings,
        ) as websocket:
            while True:
                data = websocket.recv()
                self._process_messages(data)
