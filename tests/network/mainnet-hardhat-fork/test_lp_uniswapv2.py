import brownie
import pytest
from brownie import ZERO_ADDRESS, Contract, interface
from eth_account import Account
from web3 import Web3

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp(invoker, deployer, CLPUniswapV2):
    contract = deployer.deploy(CLPUniswapV2)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def test_deposit(invoker, cmove, alice, clp, uni_router):
    assets = get_chain()["assets"]
    WETH = [asset for asset in assets if asset["symbol"] == "WETH"][0]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]
    weth = Contract.from_abi(WETH["name"], WETH["address"], interface.ERC20Detailed.abi)
    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)

    if uni_router._name == "uniswap router":
        lp_address = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
    elif uni_router._name == "sushiswap router":
        lp_address = "0x397ff1542f962076d0bfe58ea045ffa2d347aca0"
    lp_token = Contract.from_abi(
        "WETH-USDC LP Token",
        lp_address,
        interface.IUniswapV2Pair.abi,
    )

    weth_amount = 1e18
    reserves = lp_token.getReserves()  # (usdc, weth)
    usdc_amount = int(reserves[0] / reserves[1] * weth_amount)

    slippage = 0.01  # 1%

    min_weth_amount = weth_amount * (1 - slippage)
    min_usdc_amount = usdc_amount * (1 - slippage)

    # do approvals
    weth.approve(invoker.address, weth_amount, {"from": alice})
    usdc.approve(invoker.address, usdc_amount, {"from": alice})

    # Mint tokens for user
    mint_tokens_for(weth, alice.address, weth_amount)
    mint_tokens_for(usdc, alice.address, usdc_amount)

    # build invoker command
    calldata_move_weth = cmove.moveERC20In.encode_input(weth.address, weth_amount)
    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc.address, usdc_amount)
    calldata_deposit = clp.deposit.encode_input(
        weth_amount,
        weth,
        usdc_amount,
        usdc,
        (uni_router, min_weth_amount, min_usdc_amount, alice, 0),
    )

    assert lp_token.balanceOf(alice) == 0

    invoker.invoke(
        [cmove, cmove, clp],
        [calldata_move_weth, calldata_move_usdc, calldata_deposit],
        {"from": alice},
    )

    assert lp_token.balanceOf(alice) >= 1


def test_permit(invoker, clp, sign_eip2612_permit, chain):
    lp_token = Contract.from_abi(
        "WETH-USDC LP Token",
        "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",
        interface.IUniswapV2Pair.abi,
    )
    owner = Account.create()
    deadline = chain.time() + 1000
    sig = sign_eip2612_permit(lp_token, owner, invoker.address, deadline=deadline)
    v, hex_r, hex_s = Web3.toInt(sig[-1]), Web3.toHex(sig[:32]), Web3.toHex(sig[32:64])

    clp.eip2612Permit(lp_token, owner.address, invoker, 2**256 - 1, deadline, v, hex_r, hex_s)


@pytest.mark.parametrize("receiver", [ZERO_ADDRESS, "user"])
def test_withdraw(chain, sign_eip2612_permit, invoker, clp, cmove, receiver):
    # setup assets
    assets = get_chain()["assets"]
    WETH = [asset for asset in assets if asset["symbol"] == "WETH"][0]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]
    weth = Contract.from_abi(WETH["name"], WETH["address"], interface.ERC20Detailed.abi)
    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)

    alice = Account.create()
    if receiver == "user":
        receiver = alice.address
    # mint for alice
    # approx ~100 usd liquidity
    lp_token = Contract.from_abi(
        "WETH-USDC LP Token",
        "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",
        interface.IUniswapV2Pair.abi,
    )
    amount_in = int(1e12)
    lp_token.transfer(
        alice.address, amount_in, {"from": "0x03ae53b33feeac1222c3f372f32d37ba95f0f099"}
    )

    # calculate minimum received
    pool_share = amount_in / lp_token.totalSupply()
    reserves = lp_token.getReserves()  # (usdc, weth)
    slippage = 0.01  # 1% slippage
    min_usdc = int((1 - slippage) * reserves[0] * pool_share)
    min_weth = int((1 - slippage) * reserves[1] * pool_share)

    # prepare signature for permit
    deadline = chain.time() + 1000
    sig = sign_eip2612_permit(
        lp_token, alice, invoker.address, deadline=deadline, allowance=amount_in
    )
    v, hex_r, hex_s = Web3.toInt(sig[-1]), Web3.toHex(sig[:32]), Web3.toHex(sig[32:64])

    # compose invoker transaction
    calldata_permit = clp.eip2612Permit.encode_input(
        lp_token, alice.address, invoker, amount_in, deadline, v, hex_r, hex_s
    )
    calldata_move_in = cmove.moveERC20In.encode_input(lp_token, amount_in)
    calldata_withdraw = clp.withdraw.encode_input(
        lp_token, amount_in, (min_usdc, min_weth, receiver, 0)
    )

    invoker.invoke(
        [clp, cmove, clp],
        [calldata_permit, calldata_move_in, calldata_withdraw],
        {"from": alice.address},
    )

    if receiver == ZERO_ADDRESS:
        output_user = invoker.address
    else:
        output_user = alice.address

    assert weth.balanceOf(output_user) > min_weth
    assert usdc.balanceOf(output_user) > min_usdc


def test_expired_withdraw(chain, sign_eip2612_permit, invoker, clp, cmove):
    alice = Account.create()
    # mint for alice
    # approx ~100 usd liquidity
    lp_token = Contract.from_abi(
        "WETH-USDC LP Token",
        "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",
        interface.IUniswapV2Pair.abi,
    )
    amount_in = int(1e12)
    lp_token.transfer(
        alice.address, amount_in, {"from": "0x03ae53b33feeac1222c3f372f32d37ba95f0f099"}
    )

    # prepare signature for permit
    permit_deadline = chain.time() + 100
    sig = sign_eip2612_permit(
        lp_token, alice, invoker.address, deadline=permit_deadline, allowance=amount_in
    )
    v, hex_r, hex_s = Web3.toInt(sig[-1]), Web3.toHex(sig[:32]), Web3.toHex(sig[32:64])

    # compose invoker transaction
    calldata_permit = clp.eip2612Permit.encode_input(
        lp_token, alice.address, invoker, amount_in, permit_deadline, v, hex_r, hex_s
    )
    # deadline in past
    expired_deadline = chain.time() - 100
    calldata_move_in = cmove.moveERC20In.encode_input(lp_token, amount_in)
    calldata_withdraw = clp.withdraw.encode_input(
        lp_token, amount_in, (0, 0, alice.address, expired_deadline)
    )

    with brownie.reverts("CLPUniswapV2: EXPIRED"):
        invoker.invoke(
            [clp, cmove, clp],
            [calldata_permit, calldata_move_in, calldata_withdraw],
            {"from": alice.address},
        )


def test_withdraw_via_approve(alice, invoker, clp, cmove):
    # setup assets
    assets = get_chain()["assets"]
    WETH = [asset for asset in assets if asset["symbol"] == "WETH"][0]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]
    weth = Contract.from_abi(WETH["name"], WETH["address"], interface.ERC20Detailed.abi)
    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)

    # mint for alice
    # approx ~100 usd liquidity
    lp_token = Contract.from_abi(
        "WETH-USDC LP Token",
        "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",
        interface.IUniswapV2Pair.abi,
    )
    amount_in = int(1e12)
    lp_token.transfer(
        alice.address, amount_in, {"from": "0x03ae53b33feeac1222c3f372f32d37ba95f0f099"}
    )

    # approve the LP token rather than using permit
    lp_token.approve(invoker, amount_in, {"from": alice})

    calldata_move_in = cmove.moveERC20In.encode_input(lp_token, amount_in)
    calldata_withdraw = clp.withdraw.encode_input(lp_token, amount_in, (0, 0, alice, 0))

    invoker.invoke(
        [cmove, clp],
        [calldata_move_in, calldata_withdraw],
        {"from": alice.address},
    )

    assert weth.balanceOf(alice) > 0
    assert usdc.balanceOf(alice) > 0
