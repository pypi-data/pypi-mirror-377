import time
import asyncio
from typing import Optional, Any



class TTLDict:
    def __init__(self, default_ttl: int = 60, cleanup_interval: int = 300):
        """
        :param default_ttl: TTL по умолчанию (сек), если при записи не указан
        :param cleanup_interval: периодическая очистка от просроченных ключей (сек), по умолчанию 5 мин
        """

        self._store = {}
        self._default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._task = None

    def set(self, key, value, ttl: Optional[int] = None):
        if ttl is None:
            ttl = self._default_ttl
        expire_at = time.monotonic() + ttl
        self._store[key] = (value, expire_at)

        if self._task is None:
            loop = asyncio.get_running_loop()
            self._task = loop.create_task(self._cleanup_worker())

    def get(self, key):
        now = time.monotonic()
        item = self._store.get(key)
        if not item:
            return None

        value, expire_at = item
        if expire_at < now:
            del self._store[key]
            return None
        return value

    def __setitem__(self, key, value):
        self.set(key, value, self._default_ttl)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return self.get(key) is not None

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return f"<TTLDict size={len(self._store)}>"

    async def _cleanup_worker(self):
        while True:
            await asyncio.sleep(self._cleanup_interval)
            self.cleanup()

    def cleanup(self):
        """Удалить все просроченные ключи"""
        now = time.monotonic()
        expired = [k for k, (_, exp) in self._store.items() if exp < now]
        for k in expired:
            self._store.pop(k, None)

    async def stop(self):
        """Остановить фон очистки"""
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    def pop(self, key: Any) -> Any:
        return self._store.pop(key)