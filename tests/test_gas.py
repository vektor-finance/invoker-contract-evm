import pytest
from brownie import Contract, interface


@pytest.fixture(scope="module")
def btc():
    yield Contract.from_abi(
        "BTC", "0x321162cd933e2be498cd2267a90534a804051b11", interface.IERC20.abi
    )


def test_ordinary_swap(invoker, cswap, wnative, btc, alice):
    """
    Invoker <Contract>
       ├─ invoke      -  avg:  154032  avg (confirmed):  154032  low:  154032  high:  154032
    """
    wnative.deposit({"from": alice, "value": "1 ether"})
    wnative.transfer(invoker.address, "1 ether", {"from": alice})
    calldata = cswap.swapUniswapIn.encode_input("1 ether", 0, [wnative.address, btc.address])
    invoker.invoke([cswap.address], [calldata], {"from": alice, "value": "1 ether"})


def test_venue_swap(invoker, cswap_venue, wnative, btc, alice):
    """
    Invoker <Contract>
      ├─ invoke      -  avg:  110054  avg (confirmed):  110054  low:   63815  high:  156294
    """
    wnative.deposit({"from": alice, "value": "1 ether"})
    wnative.transfer(invoker.address, "1 ether", {"from": alice})
    calldata = cswap_venue.swapUniswapIn.encode_input("1 ether", 0, [wnative.address, btc.address])
    invoker.invoke([cswap_venue.address], [calldata], {"from": alice, "value": "1 ether"})
