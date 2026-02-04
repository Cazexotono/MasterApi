from fastapi.testclient import TestClient
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from src.app.fastapi import app

@pytest.fixture
def fastapi_client():
    return TestClient(app)





@pytest.fixture
def sample_rsa_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key