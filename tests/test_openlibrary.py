"""Tests for OpenLibraryClient adapter."""

from __future__ import annotations

from unittest.mock import MagicMock
import httpx
from phosphene.refverify.adapters.openlibrary import OpenLibraryClient


def test_openlibrary_search_parsing():
    fake_json = {
        "docs": [
            {
                "title": "Culture and the Evolutionary Process",
                "author_name": ["Robert Boyd", "Peter J. Richerson"],
                "first_publish_year": 1985,
                "isbn": ["9780226042176"],
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_json
    mock_resp.raise_for_status = MagicMock()

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_resp

    client = OpenLibraryClient(client=mock_client)
    cands = client.search(title="Culture and the Evolutionary Process", author="Boyd")

    assert len(cands) == 1
    assert cands[0].title == "Culture and the Evolutionary Process"
    assert cands[0].authors == ("Robert Boyd", "Peter J. Richerson")
    assert cands[0].year == 1985
    assert cands[0].source == "openlibrary"
    assert "9780226042176" in cands[0].venue
