from enum import IntEnum

from data.test_helpers import mint_tokens_for


class InterestRateMode(IntEnum):
    STABLE = 1
    VARIABLE = 2


def test_supply(clend_aavev2, invoker, alice, Contract, interface):
    token = Contract("USDC")
    atoken = Contract.from_abi(
        "aUSDC", "0xBcca60bB61934080951369a648Fb03DF4F96263C", interface.AaveToken.abi
    )

    mint_tokens_for(token, invoker, 100e6)

    calldata_supply = clend_aavev2.supply.encode_input(token, 100e6, alice)

    invoker.invoke([clend_aavev2], [calldata_supply], {"from": alice})
    assert atoken.balanceOf(alice) == 100e6


def test_withdraw(clend_aavev2, invoker, alice, Contract, interface):
    token = Contract("USDC")
    atoken = Contract.from_abi(
        "aUSDC", "0xBcca60bB61934080951369a648Fb03DF4F96263C", interface.AaveToken.abi
    )

    mint_tokens_for(atoken, invoker, 100e6)

    calldata_withdraw = clend_aavev2.withdraw.encode_input(atoken, 100e6, alice)
    invoker.invoke([clend_aavev2], [calldata_withdraw], {"from": alice})

    # this doesn't work, why?
    assert token.balanceOf(alice) == 101e6


def test_borrow_and_repay(clend_aavev2, invoker, alice, Contract, interface):
    token = Contract("USDC")
    atoken = Contract.from_abi(
        "aUSDC", "0xBcca60bB61934080951369a648Fb03DF4F96263C", interface.AaveToken.abi
    )
    data_provider = Contract.from_abi(
        "Aave Data Provider",
        "0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d",
        interface.AaveDataProvider.abi,
    )
    (_, _, variable_debt) = data_provider.getReserveTokensAddresses(token)
    variable_debt = Contract.from_abi(
        "Aave variable debt bearing USDC", variable_debt, interface.AaveDebtToken.abi
    )

    mint_tokens_for(token, invoker, 100e6)

    calldata_supply = clend_aavev2.supply.encode_input(token, 100e6, alice)

    invoker.invoke([clend_aavev2], [calldata_supply], {"from": alice})
    assert atoken.balanceOf(alice) == 100e6

    variable_debt.approveDelegation(invoker, 2**256 - 1, {"from": alice})
    calldata_borrow = clend_aavev2.borrow.encode_input(token, 1e6, InterestRateMode.VARIABLE)
    invoker.invoke([clend_aavev2], [calldata_borrow], {"from": alice})
    assert token.balanceOf(alice) == 1e6

    calldata_repay = clend_aavev2.repay.encode_input(token, 1e6, InterestRateMode.VARIABLE)
    token.transfer(invoker, 1e6, {"from": alice})
    invoker.invoke([clend_aavev2], [calldata_repay], {"from": alice})
    assert token.balanceOf(alice) == 0
