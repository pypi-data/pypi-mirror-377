import asyncio
import json
import redis.asyncio as redis

from zenx.exceptions import NoBlueprintsAvailable
from .base import SessionManager
from .types import Session
from zenx.utils import get_time



class MemorySessionManager(SessionManager):
    name = "memory"


    async def init_session_pool(self, **kwargs) -> None:
        kwargs = kwargs if kwargs else self.session_init_args
        while self.session_pool.qsize() < self.settings.SESSION_POOL_SIZE:
            session = self.client.create_session(**kwargs)
            await self.put_session(session)
        self.logger.info("initialized", session_pool_size=self.session_pool.qsize(), kwargs=kwargs, session_manager=self.name)


    async def get_session(self) -> Session:
        return self.session_pool.get_nowait()


    async def put_session(self, session: Session) -> None:
        self.session_pool.put_nowait(session)
    

    async def close_session(self, session: Session) -> None:
        await session.close()

    
    async def replace_session(self, session: Session, reason: str = "") -> Session:
        await self.close_session(session)
        new_session = self.client.create_session(**self.session_init_args)
        self.logger.debug("replaced_session", old=session.id, new=new_session.id, reason=reason, age=(get_time() - session.created_at)/1000, requests=session.requests)
        return new_session
    


class RedisSessionManager(SessionManager):
    name = "redis"


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.r = redis.Redis(host=self.settings.DB_HOST, port=self.settings.DB_PORT, password=self.settings.DB_PASS, decode_responses=True)


    async def _get_blueprints_size(self) -> int:
        return await self.r.llen(self.settings.SESSION_BLUEPRINT_REDIS_KEY)


    async def init_session_pool(self, **kwargs) -> None:
        kwargs = kwargs if kwargs else self.session_init_args
        while self.session_pool.qsize() < self.settings.SESSION_POOL_SIZE:
            config_json = await self.r.rpop(self.settings.SESSION_BLUEPRINT_REDIS_KEY)
            if not config_json:
                self.logger.info("no_blueprints_available", session_pool_size=self.session_pool.qsize(), session_manager=self.name)
                await asyncio.sleep(2)
                continue
            session = self.client.create_session(**json.loads(config_json))
            await self.put_session(session)
            self.logger.debug("updated", session_pool_size=self.session_pool.qsize(), session_manager=self.name)
        self.logger.info("initialized", session_pool_size=self.session_pool.qsize(), session_manager=self.name)


    async def get_session(self) -> Session:
        return self.session_pool.get_nowait()


    async def put_session(self, session: Session) -> None:
        self.session_pool.put_nowait(session)
    

    async def close_session(self, session: Session) -> None:
        await session.close()


    async def replace_session(self, session: Session, reason: str = "") -> Session:
        config_json = await self.r.rpop(self.settings.SESSION_BLUEPRINT_REDIS_KEY)
        if not config_json:
            self.logger.info("no_blueprints_available", session_pool_size=self.session_pool.qsize(), session_manager=self.name)
            raise NoBlueprintsAvailable()
        await self.close_session(session)
        new_session = self.client.create_session(**json.loads(config_json))
        self.logger.debug("replaced_session", old=session.id, new=new_session.id, reason=reason, age=(get_time() - session.created_at)/1000, requests=session.requests)
        return new_session