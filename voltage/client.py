from __future__ import annotations
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional
from re import search

import aiohttp

# Internal imports
from .internals import CacheHandler, HTTPHandler, WebSocketHandler

if TYPE_CHECKING:
    from .user import User

class Client:
    """
    Base voltage client.

    Attributes
    ----------
    cache_message_limit: :class:`int`
        The maximum amount of messages to cache.

    Methods
    -------
    listen:
        Registers a function to listen for an event.
    run:
        Runs the client.
    """

    def __init__(self, *, cache_message_limit: int = 5000):
        self.cache_message_limit = cache_message_limit
        self.client = aiohttp.ClientSession()
        self.http: HTTPHandler
        self.ws: WebSocketHandler
        self.listeners: Dict[str, Callable[..., Any]] = {}
        self.raw_listeners: Dict[str, Callable[[Dict], Any]] = {}
        self.loop = get_event_loop()
        self.cache: CacheHandler
        self.user: User

    def listen(self, event: str, *, raw: Optional[bool] = False):
        """
        Registers a function to listen for an event.

        Parameters
        ----------
        func: Callable
            The function to call when the event is triggered.
        event: str
            The event to listen for.
        raw: bool
            Whether or not to listen for raw events.

        Examples
        --------

        .. code-block:: python3

            @client.listen("message")
            async def any_name_you_want(message):
                if message.content == "ping":
                    await message.channel.send("pong")

            # example of a raw event
            @client.listen("message", raw=True)
            async def raw(payload):
                if payload["content"] == "ping":
                    await client.http.send_message(payload["channel"], "pong")

        """

        def inner(func: Callable[..., Any]):
            if raw:
                self.raw_listeners[event.lower()] = func
            else:
                self.listeners[event.lower()] = func # Why would we have more than one listener for the same event?
            return func

        return inner  # Returns the function so the user can use it by itself

    def run(self, token: str):
        """
        Run the client.

        Parameters
        ----------
        token: :class:`str`
            The bot token.
        """
        self.loop.run_until_complete(self.start(token))

    async def start(self, token: str):
        """
        Start the client.

        Parameters
        ----------
        token: :class:`str`
            The bot token.
        """
        self.http = HTTPHandler(self.client, token)
        self.cache = CacheHandler(self.http, self.loop, self.cache_message_limit)
        self.ws = WebSocketHandler(self.client, self.http, self.cache, token, self.dispatch, self.raw_dispatch)
        self.user = self.cache.add_user(await self.http.fetch_self())
        await self.ws.connect()

    async def dispatch(self, event: str, *args, **kwargs):
        event = event.lower()
        if func := self.listeners.get(event):
            await func(*args, **kwargs)

    async def raw_dispatch(self, payload: Dict[Any, Any]):
        event = payload["type"].lower()  # Subject to change
        if func := self.raw_listeners.get(event):
            await func(payload)

    async def get_user(self, user: str) -> Optional[User]:
        """
        Fetches a user from the cache.

        Parameters
        ----------
        user_id: :class:`int`
            The user's ID, mention or name.

        Returns
        -------
        Optional[:class:`User`]
            The user.
        """
        if match := search(r"[0-9A-HJ-KM-NP-TV-Z]{26}", user):
            return self.cache.get_user(match.group(0))
        try:
            return self.cache.get_user(user, "name")
        except ValueError:
            return None
        
