def test_healthcheck(live_client):
    health = live_client.healthcheck()
    assert isinstance(health, dict)
    assert 'status' in health