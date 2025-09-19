from __future__ import annotations

from typing import Any, Mapping, Optional

from dependency_injector import containers, providers

from nlbone.adapters.auth.keycloak import KeycloakAuthService
from nlbone.adapters.auth.token_provider import ClientTokenProvider
from nlbone.adapters.cache.async_redis import AsyncRedisCache
from nlbone.adapters.cache.memory import InMemoryCache
from nlbone.adapters.cache.redis import RedisCache
from nlbone.adapters.db.postgres import AsyncSqlAlchemyUnitOfWork, SqlAlchemyUnitOfWork
from nlbone.adapters.db.postgres.engine import get_async_session_factory, get_sync_session_factory
from nlbone.adapters.http_clients import PricingService
from nlbone.adapters.http_clients.uploadchi import UploadchiClient
from nlbone.adapters.http_clients.uploadchi.uploadchi_async import UploadchiAsyncClient
from nlbone.adapters.messaging import InMemoryEventBus
from nlbone.config.settings import Settings
from nlbone.core.ports import EventBusPort
from nlbone.core.ports.cache import AsyncCachePort, CachePort
from nlbone.core.ports.files import AsyncFileServicePort, FileServicePort


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(strict=False)

    sync_session_factory = providers.Singleton(get_sync_session_factory)
    async_session_factory = providers.Singleton(get_async_session_factory)

    # --- UoW ---
    uow = providers.Factory(SqlAlchemyUnitOfWork, session_factory=sync_session_factory)
    async_uow = providers.Factory(AsyncSqlAlchemyUnitOfWork, session_factory=async_session_factory)

    # --- Event bus ---
    event_bus: providers.Singleton[EventBusPort] = providers.Singleton(InMemoryEventBus)

    # --- Services ---
    auth: providers.Singleton[KeycloakAuthService] = providers.Singleton(KeycloakAuthService, settings=config)
    token_provider = providers.Singleton(ClientTokenProvider, auth=auth, skew_seconds=30)
    file_service: providers.Singleton[FileServicePort] = providers.Singleton(
        UploadchiClient, token_provider=token_provider
    )
    afiles_service: providers.Singleton[AsyncFileServicePort] = providers.Singleton(
        UploadchiAsyncClient, token_provider=token_provider
    )
    pricing_service: providers.Singleton[PricingService] = providers.Singleton(
        PricingService, token_provider=token_provider
    )

    cache: providers.Singleton[CachePort] = providers.Selector(
        config.CACHE_BACKEND,
        memory=providers.Singleton(InMemoryCache),
        redis=providers.Singleton(RedisCache, url=config.REDIS_URL),
    )

    async_cache: providers.Singleton[AsyncCachePort] = providers.Selector(
        config.CACHE_BACKEND,
        memory=providers.Singleton(InMemoryCache),
        redis=providers.Singleton(AsyncRedisCache, url=config.REDIS_URL),
    )


def create_container(settings: Optional[Any] = None) -> Container:
    c = Container()
    if settings is not None:
        if isinstance(settings, Settings):
            c.config.override(settings)
        elif hasattr(settings, "model_dump"):
            c.config.from_dict(settings.model_dump())  # Pydantic v2
        elif hasattr(settings, "dict"):
            c.config.from_dict(settings.dict())  # Pydantic v1
        elif isinstance(settings, Mapping):
            c.config.from_dict(dict(settings))
    return c
