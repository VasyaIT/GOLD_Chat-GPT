from typing import Callable, Any

from aiogram import Dispatcher
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.exceptions import Throttled
from aioredis import Redis

import config


r = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


def wait_answer_by_gpt(func):
    async def wrapper(message: Message) -> Callable[[Message], Any] | None:
        user_id = message.from_user.id
        if await r.get(f'ask:{user_id}'):
            await r.close()
            return
        await r.set(f'ask:{user_id}', 'true', 110)
        return await func(message)
    return wrapper


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 2, key_prefix: str = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(AntiFloodMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict) -> None | CancelHandler:
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled:
            raise CancelHandler()


def rate_limit(limit: int, key=None):
    def decorator(func):
        setattr(func, "throttling_rate_limit", limit)
        if key:
            setattr(func, "throttling_key", key)
        return func

    return decorator
