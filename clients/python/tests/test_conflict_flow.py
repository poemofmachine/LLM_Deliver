import json
import unittest
from unittest import mock

from clients.python import fetch_memory as fm


class SyncFlowTests(unittest.TestCase):

    def test_describe_revision_change_detects_new_revision(self):
        previous = "rev-1"
        current = "rev-2"
        message = fm.describe_revision_change(previous, current)
        self.assertIn("rev-2", message)
        self.assertIn("rev-1", message)

    @mock.patch("clients.python.fetch_memory.urllib.request.urlopen")
    def test_request_handoff_json_success(self, mock_urlopen):
        payload = {"demo": "ok"}
        fake_response = mock.MagicMock()
        fake_response.read.return_value = json.dumps(payload).encode("utf-8")
        fake_response.__enter__.return_value = fake_response
        mock_urlopen.return_value = fake_response

        data = fm.request_handoff_json("https://example.com", "token")
        self.assertEqual(data, payload)

    @mock.patch("clients.python.fetch_memory.urllib.request.urlopen")
    def test_request_handoff_json_invalid_payload(self, mock_urlopen):
        fake_response = mock.MagicMock()
        fake_response.read.return_value = b"<html>"
        fake_response.__enter__.return_value = fake_response
        mock_urlopen.return_value = fake_response

        with self.assertRaises(RuntimeError):
            fm.request_handoff_json("https://example.com", "token")


if __name__ == "__main__":
    unittest.main()
