import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp_curve(invoker, deployer, CLPCurve):
    contract = deployer.deploy(CLPCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


params_3pool = (
    ["DAI", "USDC", "USDT"],
    "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7",
    "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490",
    "0xd632f22692fac7611d2aa1c0d552930d43caed3b",
)


@pytest.mark.parametrize("tokens,curve_pool,lp_token,lp_benefactor", [params_3pool])
class TestBasePool:
    def test_deposit(
        self, tokens, curve_pool, lp_token, alice, invoker, cmove, clp_curve, lp_benefactor
    ):
        assets = get_chain()["assets"]
        token_contracts = []
        token_amounts = []
        calldatas = []
        for token in tokens:
            _token = [asset for asset in assets if asset["symbol"] == token][0]
            _contract = interface.ERC20Detailed(_token["address"])
            _amount = 100 * 10 ** _token["decimals"]
            token_contracts.append(_contract)
            token_amounts.append(_amount)
            _contract.approve(invoker.address, _amount, {"from": alice})
            mint_tokens_for(_contract, alice.address)
            calldatas.append(cmove.moveERC20In.encode_input(_contract, _amount))

        curve_pool = interface.ICurvePool(curve_pool)

        # need to specify which function due to function overloading
        expected_amount = curve_pool.calc_token_amount[f"uint256[{len(tokens)}],bool"](
            token_amounts, True
        )
        min_amount = expected_amount // 1.01

        # dai, usdc, usdt
        calldata_deposit = clp_curve.deposit.encode_input(
            token_amounts,
            token_contracts,
            curve_pool,
            [min_amount],
        )

        invoker.invoke(
            [*[cmove] * len(tokens), clp_curve],
            [*calldatas, calldata_deposit],
            {"from": alice},
        )

        lp_token = interface.ERC20Detailed(lp_token)

        assert lp_token.balanceOf(invoker) >= min_amount

    def test_withdraw(
        self, invoker, cmove, alice, clp_curve, tokens, curve_pool, lp_token, lp_benefactor
    ):
        assets = get_chain()["assets"]

        curve_pool = interface.CurvePool(curve_pool)
        lp_token = interface.ERC20Detailed(lp_token)

        lp_amount = 100e18
        lp_ratio = lp_amount / lp_token.totalSupply()

        token_contracts = []
        pool_balances = []
        min_tokens_received = []
        for key, token in enumerate(tokens):
            _token = [asset for asset in assets if asset["symbol"] == token][0]
            _contract = interface.ERC20Detailed(_token["address"])
            token_contracts.append(_contract)
            _balance = curve_pool.balances(key)
            pool_balances.append(_balance)
            min_tokens_received.append(lp_ratio * _balance * 0.99)

        lp_token.transfer(alice, lp_amount, {"from": lp_benefactor})
        lp_token.approve(invoker, lp_amount, {"from": alice})

        calldata_move = cmove.moveERC20In.encode_input(lp_token, lp_amount)
        calldata_withdraw = clp_curve.withdraw.encode_input(
            curve_pool,
            lp_amount,
            min_tokens_received,
        )

        invoker.invoke([cmove, clp_curve], [calldata_move, calldata_withdraw], {"from": alice})

        for token, min_received in zip(token_contracts, min_tokens_received):
            assert token.balanceOf(invoker) >= min_received


class TestUnderlyingPool:
    pass


def test_deposit_zap(invoker, cmove, clp_curve, alice):
    assets = get_chain()["assets"]
    DAI = [asset for asset in assets if asset["symbol"] == "DAI"][0]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]

    dai = Contract.from_abi(DAI["name"], DAI["address"], interface.ERC20Detailed.abi)
    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)

    curve_compound = "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56"
    curve_pool = Contract.from_abi("Compound pool", curve_compound, interface.ICurvePool.abi)
    curve_zap = "0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06"

    dai_amount = 100e18
    usdc_amount = 100e6

    dai.approve(invoker.address, dai_amount, {"from": alice})
    usdc.approve(invoker.address, usdc_amount, {"from": alice})

    mint_tokens_for(usdc, alice.address)
    mint_tokens_for(dai, alice.address)

    calldata_move_dai = cmove.moveERC20In.encode_input(dai.address, dai_amount)
    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc.address, usdc_amount)

    cdai = interface.CToken("0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643")
    cusdc = interface.CToken("0x39AA39c021dfbaE8faC545936693aC917d5E7563")

    # To calculate your balance in the underlying asset,
    # multiply your cToken balance by exchangeRateStored, and divide by 1e18.
    cdai_amount = int(dai_amount * 1e18 / cdai.exchangeRateStored())
    cusdc_amount = int(usdc_amount * 1e18 / cusdc.exchangeRateStored())

    # need to specify which function due to function overloading
    expected_amount = curve_pool.calc_token_amount["uint256[2],bool"](
        [cdai_amount, cusdc_amount], True
    )
    min_amount = expected_amount // 1.01

    # dai, usdc, usdt
    calldata_deposit = clp_curve.depositZap.encode_input(
        [dai_amount, usdc_amount],
        [dai, usdc],
        curve_zap,
        [min_amount],
    )

    invoker.invoke(
        [cmove, cmove, clp_curve],
        [calldata_move_usdc, calldata_move_dai, calldata_deposit],
        {"from": alice},
    )

    token_compound = interface.ERC20Detailed("0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2")

    assert token_compound.balanceOf(invoker) >= min_amount


def test_withdraw_zap(invoker, cmove, alice, clp_curve):
    assets = get_chain()["assets"]
    DAI = [asset for asset in assets if asset["symbol"] == "DAI"][0]
    USDC = [asset for asset in assets if asset["symbol"] == "USDC"][0]

    dai = Contract.from_abi(DAI["name"], DAI["address"], interface.ERC20Detailed.abi)
    usdc = Contract.from_abi(USDC["name"], USDC["address"], interface.ERC20Detailed.abi)

    curve_compound = "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56"
    curve_pool = Contract.from_abi(
        "Compound pool",
        curve_compound,
        [
            {
                "constant": True,
                "gas": 2250,
                "inputs": [{"name": "arg0", "type": "int128"}],
                "name": "balances",
                "outputs": [{"name": "out", "type": "uint256"}],
                "payable": False,
                "type": "function",
            }
        ],
    )
    curve_zap = "0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06"
    token_compound = interface.ERC20Detailed("0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2")
    whale_compound = "0x7ca5b0a2910b33e9759dc7ddb0413949071d7575"

    cdai = interface.CToken("0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643")
    cusdc = interface.CToken("0x39AA39c021dfbaE8faC545936693aC917d5E7563")

    # To calculate your balance in the underlying asset,
    # multiply your cToken balance by exchangeRateStored, and divide by 1e18.
    dai_total_balance = curve_pool.balances(0) * cdai.exchangeRateStored() / 1e18
    usdc_total_balance = curve_pool.balances(1) * cusdc.exchangeRateStored() / 1e18

    lp_amount = 100e18
    lp_ratio = lp_amount / token_compound.totalSupply()

    min_dai_received = int(lp_ratio * dai_total_balance * 0.99)
    min_usdc_received = int(lp_ratio * usdc_total_balance * 0.99)

    # mint LP tokens for alice
    token_compound.transfer(alice, lp_amount, {"from": whale_compound})

    token_compound.approve(invoker, lp_amount, {"from": alice})

    calldata_move_in = cmove.moveERC20In.encode_input(token_compound, lp_amount)
    calldata_withdraw_zap = clp_curve.withdrawZap.encode_input(
        token_compound, curve_zap, lp_amount, [min_dai_received, min_usdc_received]
    )

    invoker.invoke([cmove, clp_curve], [calldata_move_in, calldata_withdraw_zap], {"from": alice})
    assert dai.balanceOf(invoker) >= min_dai_received
    assert usdc.balanceOf(invoker) >= min_usdc_received
