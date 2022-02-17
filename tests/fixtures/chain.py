import pytest

from data.chain import get_chain

_connected_chain = get_chain()


@pytest.fixture(scope="session")
def connected_chain():
    return _connected_chain
