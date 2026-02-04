from typing import Optional

import httpx
from mimesis import Generic

from .fake_base_client import FakeBaseClient


class FakeUser(FakeBaseClient):
    def __init__(
        self, 
        api_url: Optional[httpx.URL],
        
        ) -> None:
        super().__init__(api_url)