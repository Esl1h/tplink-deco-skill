"""Black-box tests for the deco CLI. No router needed.

The tests cover CLI plumbing: help, environment validation and input
validation. The one test that needs the tplink-deco-api package talks to an
unreachable host and expects a clean transport error.
"""

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "deco.py"
SDK_INSTALLED = importlib.util.find_spec("tplink_deco_api") is not None


def run_cli(args, env=None):
    # Strip DECO_* so local configuration never leaks into the tests.
    environment = {k: v for k, v in os.environ.items() if not k.startswith("DECO_")}
    if env:
        environment.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=environment,
        timeout=60,
    )


class HelpTest(unittest.TestCase):
    def test_help_lists_commands(self):
        result = run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        for command in ("status", "nodes", "clients", "block", "reservations"):
            self.assertIn(command, result.stdout)


class EnvTest(unittest.TestCase):
    def test_missing_credentials_fails_before_any_network(self):
        result = run_cli(["clients"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("DECO_USER", result.stderr)
        self.assertIn("DECO_PASSWORD", result.stderr)


class InputValidationTest(unittest.TestCase):
    def test_rejects_a_malformed_mac(self):
        result = run_cli(
            ["reserve", "not-a-mac", "192.168.68.50"],
            env={"DECO_USER": "user@example.com", "DECO_PASSWORD": "pw"},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a MAC address", result.stderr)

    def test_rejects_a_malformed_ipv4(self):
        result = run_cli(
            ["reserve", "AA:BB:CC:DD:EE:FF", "999.1.1.1"],
            env={"DECO_USER": "user@example.com", "DECO_PASSWORD": "pw"},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("not an IPv4 address", result.stderr)


@unittest.skipUnless(SDK_INSTALLED, "tplink-deco-api is not installed")
class ConnectionTest(unittest.TestCase):
    def test_unreachable_host_reports_transport_error(self):
        result = run_cli(
            ["clients"],
            env={"DECO_HOST": "127.0.0.1:1", "DECO_USER": "user@example.com", "DECO_PASSWORD": "pw"},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot reach the router", result.stderr)
        self.assertIn("DECO_HOST", result.stderr)


if __name__ == "__main__":
    unittest.main()
