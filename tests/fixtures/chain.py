import pytest

from data.chain import get_chain


@pytest.fixture(scope="session")
def connected_chain():
    return get_chain()
