from brownie import CLPCurve, Invoker, accounts, interface, web3

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_token
from data.test_helpers import mint_tokens_for


def main():
    user = accounts[0]
    usdc = interface.ERC20Detailed(get_chain_token("USDC")["address"])
    dai = interface.ERC20Detailed(get_chain_token("DAI")["address"])
    usdt = interface.ERC20Detailed(get_chain_token("USDT")["address"])

    mint_tokens_for(usdc, user, 1000e6)
    mint_tokens_for(usdt, user, 1000e6)
    mint_tokens_for(dai, user, 1000e18)

    deployer = accounts.at("0x3302dBdD355fDfA7A439598885E189a4E9ad6B9b", force=True)
    clp_curve = deployer.deploy(CLPCurve)
    invoker = Invoker.at("0x805337bC5195f2BfEa531665eDa46516fa493949")
    invoker.grantRole(APPROVED_COMMAND, clp_curve, {"from": deployer})

    web3.provider.make_request("evm_setIntervalMining", [1000])
