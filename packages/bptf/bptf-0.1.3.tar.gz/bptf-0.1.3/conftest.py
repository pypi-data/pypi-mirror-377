from os import getenv

import pytest
from dotenv import load_dotenv

assert load_dotenv()

BACKPACK_TF_TOKEN = getenv("BACKPACK_TF_TOKEN")


@pytest.fixture
def backpack_tf_token() -> str:
    return BACKPACK_TF_TOKEN
