import pytest

from brownie import Invoker, accounts, Contract

@pytest.fixture(scope="module")
def invoker():
    return accounts[0].deploy(Invoker)

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

@pytest.mark.require_network("mainnet-fork")
def test_buy_dai(user, dai, WETH, uni_router):
    path = [WETH.address, dai.address]
    uni_router.swapExactETHForTokens(2700 * 1e18, path, user, 1659715115, {'from': user, 'value': 1e18})
    assert dai.balanceOf(user) > 2700 * 1e18

@pytest.mark.require_network("mainnet-fork")
def test_buy_dai_via_invoker(user, dai, WETH, uni_router, invoker):
    path = [WETH.address, dai.address]
    calldata = uni_router.swapExactETHForTokens.encode_input(2700 * 1e18, path, user, 1659715115)
    invoker.invoke(uni_router.address, calldata, 1e18, {'from': user, 'value': 1e18})
    assert dai.balanceOf(user) > 2700 * 1e18

@pytest.mark.require_network("mainnet-fork")
def test_buy_dai_via_delegate_invoker(user, dai, WETH, uni_router, invoker):
    path = [WETH.address, dai.address]
    calldata = uni_router.swapExactETHForTokens.encode_input(2700 * 1e18, path, user, 1659715115)
    invoker.invokeDelegate(uni_router.address, calldata, {'from': user, 'value': 1e18})
    assert dai.balanceOf(user) > 2700 * 1e18
