from __future__ import annotations

import reprompt


def test_init():
    """Test the init function returns a RepromptClient."""
    client = reprompt.init(api_key="test-key", org_slug="test-hp")

    assert isinstance(client, reprompt.RepromptClient)
    assert client.api_key == "test-key"
    assert client.org_slug == "test-hp"
    assert client.base_url == "https://api.repromptai.com/v1"

    client.close()
