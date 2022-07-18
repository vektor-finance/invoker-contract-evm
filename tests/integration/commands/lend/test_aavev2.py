from data.test_helpers import mint_tokens_for


def test_deposit(clend_aavev2, invoker, alice, Contract, interface):
    token = Contract("USDC")
    atoken = Contract.from_abi(
        "aUSDC", "0xBcca60bB61934080951369a648Fb03DF4F96263C", interface.ERC20Detailed.abi
    )

    mint_tokens_for(token, invoker, 100e6)

    calldata_deposit = clend_aavev2.deposit.encode_input(token, 100e6, alice)

    invoker.invoke([clend_aavev2], [calldata_deposit], {"from": alice})
    assert atoken.balanceOf(alice) == 100e6
