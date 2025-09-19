def test_licensing(live_client):
    license_info = live_client.licensing.status
    assert isinstance(license_info, dict)
    assert 'expiryDate' in license_info
    assert 'isLicensed' in license_info