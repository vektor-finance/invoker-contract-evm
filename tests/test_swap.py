import pytest

from brownie import Invoker, accounts, Contract

@pytest.fixture(scope="module")
def invoker():
    return accounts[0].deploy(Invoker)

# def test_buy_dai(user, dai, WETH, uni_router):
#     path = [WETH.address, dai.address]
#     uni_router.swapExactETHForTokens(0, path, user, 1659715115, {'from': user, 'value': 1e18})
#     assert dai.balanceOf(user) == 2774277753198953882774

def test_buy_dai_via_invoker(user, dai, WETH, uni_router, invoker):
    path = [WETH.address, dai.address]
    calldata = uni_router.swapExactETHForTokens.encode_input(0, path, user, 1659715115)
    invoker.invoke(uni_router.address, calldata, 1e18, {'from': user, 'value': 1e18})
    assert dai.balanceOf(user) == 2774277753198953882774
