from data.test_helpers import mint_tokens_for


def test_supply(clend_aavev2, invoker, alice, Contract, interface):
    token = Contract("USDC")
    atoken = Contract.from_abi(
        "aUSDC", "0xBcca60bB61934080951369a648Fb03DF4F96263C", interface.AaveToken.abi
    )

    mint_tokens_for(token, invoker, 100e6)

    calldata_supply = clend_aavev2.supply.encode_input(token, 100e6, alice)

    invoker.invoke([clend_aavev2], [calldata_supply], {"from": alice})
    assert atoken.balanceOf(alice) == 100e6
    print(atoken.scaledBalanceOf(alice))


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
