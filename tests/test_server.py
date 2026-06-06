from server import advertised_agent_url


def test_advertised_url_rewrites_wildcard_bind_host_to_loopback():
    assert advertised_agent_url(host="0.0.0.0", port=9009, card_url=None) == (
        "http://127.0.0.1:9009/"
    )


def test_advertised_url_prefers_explicit_card_url():
    assert advertised_agent_url(
        host="0.0.0.0",
        port=9009,
        card_url="https://example.test/agent",
    ) == "https://example.test/agent"
