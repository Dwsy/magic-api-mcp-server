import unittest

from mcp.config import MagicAPISettings


class MagicAPISettingsTest(unittest.TestCase):
    def test_defaults(self):
        settings = MagicAPISettings.from_env({})
        self.assertEqual(settings.base_url, "http://127.0.0.1:10712")
        self.assertAlmostEqual(settings.timeout_seconds, 30.0)
        self.assertFalse(settings.auth_enabled)

    def test_env_override(self):
        env = {
            "MAGIC_API_BASE_URL": "http://example.com/",
            "MAGIC_API_TIMEOUT_SECONDS": "45",
            "MAGIC_API_AUTH_ENABLED": "true",
            "MAGIC_API_USERNAME": "admin",
            "MAGIC_API_PASSWORD": "pwd",
        }
        settings = MagicAPISettings.from_env(env)
        self.assertEqual(settings.base_url, "http://example.com")
        self.assertTrue(settings.auth_enabled)
        headers = {}
        settings.inject_auth(headers)
        self.assertEqual(headers.get("Magic-Username"), "admin")
        self.assertEqual(headers.get("Magic-Password"), "pwd")
        self.assertEqual(settings.timeout_seconds, 45.0)


if __name__ == "__main__":
    unittest.main()
