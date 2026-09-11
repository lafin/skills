import unittest

from catalog_service import CatalogService


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


class CatalogServiceTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.catalog_calls = []
        self.live_calls = []

        def fetch_catalog(tenant, locale):
            self.catalog_calls.append((tenant, locale))
            return f"catalog:{tenant}:{locale}:{len(self.catalog_calls)}"

        def fetch_live_status(tenant, locale):
            self.live_calls.append((tenant, locale))
            return f"live:{tenant}:{locale}:{len(self.live_calls)}"

        self.fetch_catalog = fetch_catalog
        self.fetch_live_status = fetch_live_status

        self.service = CatalogService(
            self.fetch_catalog,
            self.fetch_live_status,
            self.clock,
            ttl_seconds=10,
            max_entries=8,
        )

    def test_cache_hit_uses_complete_tenant_and_locale_key(self):
        first = self.service.catalog("acme", "en")
        self.assertEqual(first, self.service.catalog("acme", "en"))
        self.assertNotEqual(first, self.service.catalog("beta", "en"))
        self.assertNotEqual(first, self.service.catalog("acme", "fr"))
        self.assertEqual(3, len(self.catalog_calls))

    def test_entry_expires_at_ttl(self):
        first = self.service.catalog("acme", "en")
        self.clock.now = 9
        self.assertEqual(first, self.service.catalog("acme", "en"))
        self.clock.now = 10
        self.assertNotEqual(first, self.service.catalog("acme", "en"))

    def test_invalidation_can_target_one_locale_or_one_tenant(self):
        acme_en = self.service.catalog("acme", "en")
        acme_fr = self.service.catalog("acme", "fr")
        beta_en = self.service.catalog("beta", "en")
        self.service.invalidate("acme", "en")
        self.assertNotEqual(acme_en, self.service.catalog("acme", "en"))
        self.assertEqual(beta_en, self.service.catalog("beta", "en"))
        self.service.invalidate("acme")
        self.assertNotEqual(acme_fr, self.service.catalog("acme", "fr"))
        self.assertEqual(beta_en, self.service.catalog("beta", "en"))

    def test_cache_is_bounded(self):
        service = CatalogService(
            self.fetch_catalog,
            self.fetch_live_status,
            self.clock,
            ttl_seconds=10,
            max_entries=2,
        )
        service.catalog("acme", "en")
        service.catalog("acme", "fr")
        service.catalog("beta", "en")
        calls_after_fill = len(self.catalog_calls)
        service.catalog("acme", "en")
        service.catalog("acme", "fr")
        service.catalog("beta", "en")
        self.assertGreater(len(self.catalog_calls), calls_after_fill)

    def test_live_status_route_is_never_cached(self):
        first = self.service.handle("/live-status", "acme", "en")
        second = self.service.handle("/live-status", "acme", "en")
        self.assertNotEqual(first, second)
        self.assertEqual(2, len(self.live_calls))


if __name__ == "__main__":
    unittest.main()
