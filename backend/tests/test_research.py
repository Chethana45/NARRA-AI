import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import research


def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        import requests
        resp.raise_for_status.side_effect = requests.HTTPError(f"{status_code}")
    return resp


def test_research_found():
    search_resp = _mock_response({"query": {"search": [{"title": "A. R. Rahman"}]}})
    summary_resp = _mock_response({
        "title": "A. R. Rahman",
        "description": "Indian composer",
        "extract": "A. R. Rahman is an Indian composer. He has won two Academy Awards.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/A._R._Rahman"}},
        "type": "standard",
    })
    with patch("services.research.requests.get", side_effect=[search_resp, summary_resp]):
        result = research.research("A. R. Rahman")

    assert result.found is True
    assert result.title == "A. R. Rahman"
    assert "Academy Awards" in result.extract
    assert len(result.verified_facts) >= 1
    d = result.to_dict()
    assert d["source"] == "Wikipedia"


def test_research_not_found():
    search_resp = _mock_response({"query": {"search": []}})
    with patch("services.research.requests.get", return_value=search_resp):
        result = research.research("Xyzzqqnonexistentperson123")

    assert result.found is False
    assert result.error is not None


def test_research_empty_query():
    result = research.research("   ")
    assert result.found is False


def test_research_disambiguation_treated_as_not_found():
    search_resp = _mock_response({"query": {"search": [{"title": "Mercury"}]}})
    summary_resp = _mock_response({
        "title": "Mercury",
        "type": "disambiguation",
        "extract": "Mercury may refer to:",
    })
    with patch("services.research.requests.get", side_effect=[search_resp, summary_resp]):
        result = research.research("Mercury")
    assert result.found is False
