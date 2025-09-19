import os
import pytest
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from fmeflowclient import FMEFlowClient

load_dotenv()

@pytest.fixture(scope="session")
def live_client():
    base_url = os.getenv("FMEFLOW_BASE_URL")
    token = os.getenv("FMEFLOW_TOKEN")
    verify_ssl = os.getenv("FMEFLOW_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
    return FMEFlowClient(base_url=base_url, token=token, verify_ssl=verify_ssl)
