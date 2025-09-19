import asyncio
import logging
import os

import msgspec

from ..protocol import ClientProtocol
from ..schema.items import AnyItem

logger = logging.getLogger(__name__)


class ItemCacheStorage(msgspec.Struct):
    server_version: str
    items: dict[str, AnyItem]
    constants: dict[str, float | int | str]


class ItemStorageMixin(ClientProtocol):
    async def load_items_and_constants(self) -> None:
        cache_file = "item_cache.yaml"
        if await asyncio.to_thread(os.path.exists, cache_file):
            try:
                data = await asyncio.to_thread(lambda: open(cache_file, "rb").read())
                item_cache = msgspec.yaml.decode(data, type=ItemCacheStorage)
                self._items = item_cache.items
                self._constants = item_cache.constants
                self._client_version = item_cache.server_version
            except Exception as e:
                logger.error(f"Error loading item cache: {e}")

    async def set_items_and_constants(
        self, items: dict[str, AnyItem], constants: dict[str, float | int | str]
    ) -> None:
        self._items = items
        self._constants = constants

        if not self._server_version:
            raise ValueError("server_version not set")

        item_cache = ItemCacheStorage(server_version=self._server_version, items=items, constants=constants)
        data = msgspec.yaml.encode(item_cache)
        try:
            await asyncio.to_thread(lambda: open("item_cache.yaml", "wb").write(data))
        except Exception as e:
            logger.error(f"Error saving item cache: {e}")
