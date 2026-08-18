import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "scripts" / "subscription_audit.py"
SPEC = importlib.util.spec_from_file_location("subscription_audit", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AuditTests(unittest.TestCase):
    def test_rejects_h3_on_tcp(self):
        report = MODULE.audit("vless://id@example.com:443?type=tcp&security=tls&sni=example.com&alpn=h3#bad\n")
        self.assertFalse(report["passed"])
        self.assertEqual(report["errors"][0]["code"], "h3-without-quic")

    def test_accepts_h3_on_xhttp(self):
        report = MODULE.audit("vless://id@example.com:443?type=xhttp&security=tls&sni=example.com&alpn=h3#good\n")
        self.assertTrue(report["passed"])
        self.assertTrue(report["nodes"][0]["real_h3"])

    def test_accepts_hysteria2(self):
        report = MODULE.audit("hysteria2://secret@example.com:443?sni=example.com#hy2\n")
        self.assertTrue(report["passed"])


if __name__ == "__main__":
    unittest.main()
