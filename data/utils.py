import os

from brownie import accounts


def get_signer():
    print(f"Available accounts: {accounts.load()}")
    account = accounts.load(input("Select account to sign with: "))
    print(f"Signing with {account}")
    return account


def get_opts(user, chain):
    gas_override = os.environ.get("GAS_GWEI")
    if gas_override:
        return {"from": user, "gas_price": f"{gas_override} gwei"}
    if chain.get("eip1559"):
        return {"from": user, "priority_fee": "2 gwei"}
    else:
        return {"from": user}
