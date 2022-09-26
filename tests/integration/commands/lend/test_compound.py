import pytest

from data.chain import get_chain_token
from data.test_helpers import mint_tokens_for

BASE_ASSET = "USDC"
ERRORS = {
    "0x0819bdcd": "SignatureExpired",
    "0x0dc149f0": "AlreadyInitialized",
    "0x14c5f7b6": "NotCollateralized",
    "0x1b8f24aa": "InvalidUInt104",
    "0x1d99ddbf": "NotForSale",
    "0x36405305": "BadAsset",
    "0x3d32ffdb": "TimestampTooLarge",
    "0x40622f2c": "BadSignatory",
    "0x49b9231e": "BadDiscount",
    "0x4bd574ec": "BadNonce",
    "0x4d6b3250": "LiquidateCFTooLarge",
    "0x6c76c96e": "NegativeNumber",
    "0x6e772475": "BadMinimum",
    "0x749b5939": "BadAmount",
    "0x82b42900": "Unauthorized",
    "0x8ad8cb20": "BadDecimals",
    "0x9369ae35": "InvalidInt104",
    "0x945e9268": "InsufficientReserves",
    "0x971241a1": "Absurd",
    "0x9c5b7fcf": "InvalidValueV",
    "0x9e87fac8": "Paused",
    "0xc9f5d8e4": "BorrowCFTooLarge",
    "0xcefaffeb": "TransferOutFailed",
    "0xddeb79ba": "NotLiquidatable",
    "0xdf8153c7": "TooManyAssets",
    "0xe273b446": "BorrowTooSmall",
    "0xe397a99b": "NoSelfTransfer",
    "0xe54396a2": "InvalidUInt64",
    "0xe7a3dfa0": "TransferInFailed",
    "0xe7e828ad": "InvalidInt256",
    "0xec5d4e22": "InvalidUInt128",
    "0xed9a0195": "InvalidValueS",
    "0xf58f733a": "SupplyCapExceeded",
    "0xfa6ad355": "TooMuchSlippage",
    "0xfd1ee349": "BadPrice",
    "Absurd": "0x971241a1",
    "AlreadyInitialized": "0x0dc149f0",
    "BadAmount": "0x749b5939",
    "BadAsset": "0x36405305",
    "BadDecimals": "0x8ad8cb20",
    "BadDiscount": "0x49b9231e",
    "BadMinimum": "0x6e772475",
    "BadNonce": "0x4bd574ec",
    "BadPrice": "0xfd1ee349",
    "BadSignatory": "0x40622f2c",
    "BorrowCFTooLarge": "0xc9f5d8e4",
    "BorrowTooSmall": "0xe273b446",
    "InsufficientReserves": "0x945e9268",
    "InvalidInt104": "0x9369ae35",
    "InvalidInt256": "0xe7e828ad",
    "InvalidUInt104": "0x1b8f24aa",
    "InvalidUInt128": "0xec5d4e22",
    "InvalidUInt64": "0xe54396a2",
    "InvalidValueS": "0xed9a0195",
    "InvalidValueV": "0x9c5b7fcf",
    "LiquidateCFTooLarge": "0x4d6b3250",
    "NegativeNumber": "0x6c76c96e",
    "NoSelfTransfer": "0xe397a99b",
    "NotCollateralized": "0x14c5f7b6",
    "NotForSale": "0x1d99ddbf",
    "NotLiquidatable": "0xddeb79ba",
    "Paused": "0x9e87fac8",
    "SignatureExpired": "0x0819bdcd",
    "SupplyCapExceeded": "0xf58f733a",
    "TimestampTooLarge": "0x3d32ffdb",
    "TooManyAssets": "0xdf8153c7",
    "TooMuchSlippage": "0xfa6ad355",
    "TransferInFailed": "0xe7a3dfa0",
    "TransferOutFailed": "0xcefaffeb",
    "Unauthorized": "0x82b42900",
}


def assert_approx(a, b, threshold=1):
    assert a - threshold <= b <= a + threshold


@pytest.mark.parametrize("asset", ["USDC", "WBTC", "COMP", "WETH", "LINK", "UNI"])
def test_supply_and_withdraw_user(clend_compound, asset, invoker, alice, interface):
    token = interface.ERC20Detailed(get_chain_token(asset)["address"])
    mint_amount = 1e8
    supply_amount = 1e6
    withdraw_amount = 1e5
    mint_tokens_for(token, alice, mint_amount)

    comet = interface.CompoundV3Comet("0xc3d688B66703497DAA19211EEdff47f25384cdc3")

    comet.allow(invoker, True, {"from": alice})
    token.approve(comet, mint_amount, {"from": alice})

    calldata_supply = clend_compound.supply_user.encode_input(comet, token, supply_amount, alice)
    invoker.invoke([clend_compound], [calldata_supply], {"from": alice})

    assert token.balanceOf(alice) == mint_amount - supply_amount
    balance = comet.balanceOf(alice) if asset == "USDC" else comet.userCollateral(alice, token)[0]
    assert_approx(balance, supply_amount, 2)

    calldata_withdraw = clend_compound.withdraw_user.encode_input(
        comet, token, withdraw_amount, alice
    )
    invoker.invoke([clend_compound], [calldata_withdraw], {"from": alice})

    assert token.balanceOf(alice) == mint_amount - supply_amount + withdraw_amount
    balance = comet.balanceOf(alice) if asset == "USDC" else comet.userCollateral(alice, token)[0]
    assert_approx(balance, supply_amount - withdraw_amount, 2)


@pytest.mark.parametrize("asset", ["USDC", "WBTC", "COMP", "WETH", "LINK", "UNI"])
def test_supply_and_withdraw_invoker(clend_compound, cmove, asset, invoker, alice, interface):
    token = interface.ERC20Detailed(get_chain_token(asset)["address"])
    mint_amount = 1000e6
    supply_amount = 900e6
    withdraw_amount = 800e6
    mint_tokens_for(token, alice, mint_amount)

    comet = interface.CompoundV3Comet("0xc3d688B66703497DAA19211EEdff47f25384cdc3")

    comet.allow(invoker, True, {"from": alice})
    token.approve(invoker, mint_amount, {"from": alice})

    calldata_transfer_in = cmove.moveERC20In.encode_input(token, supply_amount)
    calldata_supply = clend_compound.supply_invoker.encode_input(
        comet, token, supply_amount, invoker
    )
    calldata_transfer_out = clend_compound.transfer_asset_out.encode_input(
        comet, token, 2**256 - 1 if asset == "USDC" else supply_amount, alice
    )
    invoker.invoke(
        [cmove, clend_compound, clend_compound],
        [calldata_transfer_in, calldata_supply, calldata_transfer_out],
        {"from": alice},
    )

    assert token.balanceOf(alice) == mint_amount - supply_amount
    balance = comet.balanceOf(alice) if asset == "USDC" else comet.userCollateral(alice, token)[0]
    assert_approx(balance, supply_amount, 2)

    calldata_transfer_in2 = clend_compound.transfer_asset_in.encode_input(
        comet, token, withdraw_amount
    )
    calldata_withdraw = clend_compound.withdraw_invoker.encode_input(
        comet, token, 2**256 - 1 if asset == "USDC" else withdraw_amount, invoker
    )
    calldata_transfer_out2 = cmove.moveAllERC20Out.encode_input(token, alice)
    invoker.invoke(
        [clend_compound, clend_compound, cmove],
        [calldata_transfer_in2, calldata_withdraw, calldata_transfer_out2],
        {"from": alice},
    )

    assert_approx(token.balanceOf(alice), mint_amount - supply_amount + withdraw_amount)
    balance = comet.balanceOf(alice) if asset == "USDC" else comet.userCollateral(alice, token)[0]
    assert_approx(balance, supply_amount - withdraw_amount, 3)
