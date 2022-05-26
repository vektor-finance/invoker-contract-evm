from dataclasses import dataclass
from typing import List, Optional

import pytest
from brownie import ZERO_ADDRESS, Contract, interface

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp_curve(invoker, deployer, CLPCurve):
    contract = deployer.deploy(CLPCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@dataclass
class CurveTestCase:
    name: str
    tokens: List[str]
    pool: str
    lp_token: str
    lp_benefactor: str
    zap: Optional[str] = None

    def params(self):
        return (self.tokens, self.pool, self.lp_token, self.lp_benefactor, self.zap)


# plain pool tests

plain_3pool = CurveTestCase(
    name="3pool",
    tokens=["DAI", "USDC", "USDT"],
    pool="0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7",
    lp_token="0x6c3f90f043a72fa612cbac8115ee7e52bde6e490",
    lp_benefactor="0xd632f22692fac7611d2aa1c0d552930d43caed3b",
)

plain_slink = CurveTestCase(
    name="slink",
    tokens=["LINK", "sLINK"],
    pool="0xF178C0b5Bb7e7aBF4e12A4838C7b7c5bA2C623c0",
    lp_token="0xcee60cfa923170e4f8204ae08b4fa6a3f5656f3a",
    lp_benefactor="0xfd4d8a17df4c27c1dd245d153ccf4499e806c87d",
)

plain_pool_tests = []
plain_pool_names = []
for pool in [plain_3pool, plain_slink]:
    plain_pool_tests.append(pool.params())
    plain_pool_names.append(pool.name)

# meta/underlying pool tests

lending_compound = CurveTestCase(
    name="compound",
    tokens=["DAI", "USDC"],
    pool="0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56",
    zap="0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06",
    lp_token="0x845838df265dcd2c412a1dc9e959c7d08537f8a2",
    lp_benefactor="0x7ca5b0a2910b33e9759dc7ddb0413949071d7575",
)

lending_aave_pool = CurveTestCase(
    name="aave",
    tokens=["DAI", "USDC", "USDT"],
    pool="0xDeBF20617708857ebe4F679508E7b7863a8A8EeE",
    zap=None,
    lp_token="0xFd2a8fA60Abd58Efe3EeE34dd494cD491dC14900",
    lp_benefactor="0xd662908ada2ea1916b3318327a97eb18ad588b5d",
)

meta_busd_pool = CurveTestCase(
    name="busd",
    tokens=["DAI", "USDC", "USDT", "BUSD"],
    pool="0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27",
    lp_token="0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B",
    lp_benefactor="0x69fb7c45726cfe2badee8317005d3f94be838840",
    zap="0xb6c057591E073249F2D9D88Ba59a46CFC9B59EdB",
)


@pytest.mark.parametrize(
    "tokens,curve_pool,lp_token,lp_benefactor,curve_zap", plain_pool_tests, ids=plain_pool_names
)
class TestBasePool:
    def test_deposit(
        self,
        tokens,
        curve_pool,
        lp_token,
        alice,
        invoker,
        cmove,
        clp_curve,
        lp_benefactor,
        curve_zap,
    ):
        assets = get_chain()["assets"]
        token_contracts = []
        token_amounts = []
        calldatas = []
        for token in tokens:
            _token = [asset for asset in assets if asset["symbol"] == token][0]
            _address = _token["address"] or "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
            _contract = interface.ERC20Detailed(_address)
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
            [min_amount, ZERO_ADDRESS],
        )

        invoker.invoke(
            [*[cmove] * len(tokens), clp_curve],
            [*calldatas, calldata_deposit],
            {"from": alice},
        )

        lp_token = interface.ERC20Detailed(lp_token)

        assert lp_token.balanceOf(invoker) >= min_amount

    def test_withdraw(
        self,
        invoker,
        cmove,
        alice,
        clp_curve,
        tokens,
        curve_pool,
        lp_token,
        lp_benefactor,
        curve_zap,
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
            _address = _token["address"] or "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
            _contract = interface.ERC20Detailed(_address)
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


class UnderlyingPool:
    def test_deposit_zap(
        self,
        tokens,
        curve_pool,
        curve_zap,
        invoker,
        alice,
        cmove,
        clp_curve,
        lp_token,
        lp_benefactor,
    ):
        assets = get_chain()["assets"]
        token_contracts = []
        token_amounts = []
        calldatas = []
        for token in tokens:
            _token = [asset for asset in assets if asset["symbol"] == token][0]
            _address = _token["address"] or "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
            _contract = interface.ERC20Detailed(_address)
            _amount = 100 * 10 ** _token["decimals"]
            token_contracts.append(_contract)
            token_amounts.append(_amount)
            _contract.approve(invoker.address, _amount, {"from": alice})
            mint_tokens_for(_contract, alice.address)
            calldatas.append(cmove.moveERC20In.encode_input(_contract, _amount))

        curve_pool = interface.ICurvePool(curve_pool)
        expected_amount = self.calc_deposit(curve_pool, token_contracts, token_amounts)
        min_amount = expected_amount // 1.01

        calldata_deposit = clp_curve.depositZap.encode_input(
            token_amounts, token_contracts, curve_zap or curve_pool, [min_amount, bool(curve_zap)]
        )

        invoker.invoke(
            [*[cmove] * len(tokens), clp_curve],
            [*calldatas, calldata_deposit],
            {"from": alice},
        )

        lp_token = interface.ERC20Detailed(lp_token)
        assert lp_token.balanceOf(invoker) >= min_amount

    def test_withdraw_zap(
        self,
        tokens,
        curve_pool,
        curve_zap,
        invoker,
        alice,
        cmove,
        clp_curve,
        lp_token,
        lp_benefactor,
    ):
        assets = get_chain()["assets"]

        curve_pool = Contract.from_abi(
            "Curve Pool",
            curve_pool,
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
        lp_token = interface.ERC20Detailed(lp_token)

        lp_amount = 100e18

        token_contracts = []
        for token in tokens:
            _token = [asset for asset in assets if asset["symbol"] == token][0]
            _address = _token["address"] or "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
            _contract = interface.ERC20Detailed(_address)
            token_contracts.append(_contract)

        lp_token.transfer(alice, lp_amount, {"from": lp_benefactor})
        lp_token.approve(invoker, lp_amount, {"from": alice})

        min_tokens_received = self.calc_withdraw(curve_pool, lp_amount, lp_token)

        calldata_move = cmove.moveERC20In.encode_input(lp_token, lp_amount)
        calldata_withdraw = clp_curve.withdrawZap.encode_input(
            lp_token,
            curve_zap or curve_pool,
            lp_amount,
            [min_tokens_received, bool(curve_zap)],
        )

        invoker.invoke([cmove, clp_curve], [calldata_move, calldata_withdraw], {"from": alice})

        for token, min_received in zip(token_contracts, min_tokens_received):
            assert token.balanceOf(invoker) >= min_received


@pytest.mark.parametrize(
    "tokens,curve_pool,lp_token,lp_benefactor,curve_zap",
    [lending_compound.params()],
    ids=[lending_compound.name],
)
class TestCompoundPool(UnderlyingPool):
    def calc_deposit(self, curve_pool, token_contracts, token_amounts):
        cdai = interface.CToken("0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643")
        cusdc = interface.CToken("0x39AA39c021dfbaE8faC545936693aC917d5E7563")
        cdai_amount = int(token_amounts[0] * 1e18 / cdai.exchangeRateStored())
        cusdc_amount = int(token_amounts[1] * 1e18 / cusdc.exchangeRateStored())
        expected_amount = curve_pool.calc_token_amount["uint256[2],bool"](
            [cdai_amount, cusdc_amount], True
        )
        return int(0.99 * expected_amount)

    def calc_withdraw(self, curve_pool, lp_amount, lp_token):
        cdai = interface.CToken("0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643")
        cusdc = interface.CToken("0x39AA39c021dfbaE8faC545936693aC917d5E7563")

        # To calculate your balance in the underlying asset,
        # multiply your cToken balance by exchangeRateStored, and divide by 1e18.
        dai_total_balance = curve_pool.balances(0) * cdai.exchangeRateStored() / 1e18
        usdc_total_balance = curve_pool.balances(1) * cusdc.exchangeRateStored() / 1e18

        lp_ratio = lp_amount / lp_token.totalSupply()

        min_dai_received = int(lp_ratio * dai_total_balance * 0.99)
        min_usdc_received = int(lp_ratio * usdc_total_balance * 0.99)

        return [min_dai_received, min_usdc_received]


@pytest.mark.parametrize(
    "tokens,curve_pool,lp_token,lp_benefactor,curve_zap",
    [lending_aave_pool.params()],
    ids=[lending_aave_pool.name],
)
class TestAavePool(UnderlyingPool):
    def calc_deposit(self, curve_pool, token_contracts, token_amounts):
        # expected_amount = curve_pool.calc_token_amount
        return 0

    def calc_withdraw(self, curve_pool, lp_amount, lp_token):
        return [0, 0, 0]


@pytest.mark.parametrize(
    "tokens,curve_pool,lp_token,lp_benefactor,curve_zap",
    [meta_busd_pool.params()],
    ids=[meta_busd_pool.name],
)
class TestMetaPool(UnderlyingPool):
    def calc_deposit(self, curve_pool, token_contracts, token_amounts):
        # need to specify which function due to function overloading
        expected_amount = curve_pool.calc_token_amount[f"uint256[{len(token_contracts)}],bool"](
            token_amounts, True
        )
        return int(0.99 * expected_amount)

    def calc_withdraw(self, curve_pool, lp_amount, lp_token):
        return [0, 0, 0, 0]
