from typing import Any, Callable, Dict, Optional, Self, Union, Awaitable
from socketio import AsyncClient


class SearchParameters:
    def __init__(self) -> None:
        pass

    def to_json(self) -> None:
        pass


class Client:
    url: str = "wss://audio.nekto.me/"

    def __init__(
        self,
        token: str,
        user_agent: str,
    ) -> None:
        self.token = token
        self.user_agent = user_agent
        self.connection = AsyncClient()
        self.handlers = dict()

        self.dialog_id = None
        self._recirect_to = None
        self.media = MediaRedirect()

    def redirect_to(self, client: Self) -> None:
        self._recirect_to = client

    def get_redirect_to(self) -> Optional[Self]:
        return self._recirect_to

    def add_handler(self, name: str, callback: Union[Callable, Awaitable]) -> None:
        self.handlers.update({name: callback})

    async def dispatch(self, event: str, data: Dict[Any, str]) -> None:
        handler = self.handlers.get(event)
        if handler:
            return await handler(self, data)
        type = data.get("type")
        if data.get("type"):
            handler = self.handlers.get(type)
            if handler:
                await handler(self, data)

    async def init(self) -> None:
        headers = {
            "User-Agent": self.user_agent,
        }
        self.connection.on("*", self.dispatch)
        await self.connection.connect(
            url=self.url,
            socketio_path="websocket",
            headers=headers,
        )
