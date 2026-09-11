"""Small request router with a deliberately incomplete catalog cache."""


class CatalogService:
    def __init__(
        self,
        fetch_catalog,
        fetch_live_status,
        clock,
        *,
        ttl_seconds=30,
        max_entries=2,
    ):
        self._fetch_catalog = fetch_catalog
        self._fetch_live_status = fetch_live_status
        self._clock = clock
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._cache = {}

    def catalog(self, tenant, locale):
        # This key is incomplete, entries never expire, and the cache is unbounded.
        if locale not in self._cache:
            self._cache[locale] = self._fetch_catalog(tenant, locale)
        return self._cache[locale]

    def invalidate(self, tenant, locale=None):
        if locale is None:
            self._cache.clear()
        else:
            self._cache.pop(locale, None)

    def handle(self, route, tenant, locale):
        if route == "/catalog":
            return self.catalog(tenant, locale)
        if route == "/live-status":
            # Live status is request-specific and must not be cached.
            key = ("live-status", tenant, locale)
            if key not in self._cache:
                self._cache[key] = self._fetch_live_status(tenant, locale)
            return self._cache[key]
        raise ValueError(f"unknown route: {route}")
