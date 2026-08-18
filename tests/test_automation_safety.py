import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[1]


class AutomationSafetyTests(unittest.TestCase):
    def test_firewall_is_opt_in(self):
        defaults = (ROOT / "ansible/roles/proxy_gateway_harness/defaults/main.yml").read_text()
        self.assertIn("proxy_gateway_harness_manage_firewall: false", defaults)

    def test_installers_are_empty_by_default(self):
        defaults = (ROOT / "ansible/roles/proxy_gateway_harness/defaults/main.yml").read_text()
        self.assertIn("proxy_gateway_harness_installers: []", defaults)

    def test_installer_requires_https_checksum_and_creates(self):
        tasks = (ROOT / "ansible/roles/proxy_gateway_harness/tasks/installer.yml").read_text()
        self.assertIn('installer.url.startswith("https://")', tasks)
        self.assertIn('installer.sha256 is match("^[0-9a-fA-F]{64}$")', tasks)
        self.assertIn("installer.creates is defined", tasks)

    def test_cloud_init_is_pinned_and_does_not_pipe_to_shell(self):
        config = (ROOT / "cloud-init/proxy-gateway.yaml.example").read_text()
        self.assertIn("revision=PINNED_COMMIT", config)
        self.assertNotIn("curl | sh", config)
        self.assertNotIn("curl | bash", config)


if __name__ == "__main__":
    unittest.main()
