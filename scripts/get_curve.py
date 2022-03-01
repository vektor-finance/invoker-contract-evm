import json
import os

from brownie import Contract, interface, network

from data.chain import get_chain_from_network_name


def main():
    (chain, _) = get_chain_from_network_name(network.show_active())
    if not chain:
        raise ValueError(
            "Network not supported in config. Please review data/chains.yaml", network.show_active()
        )

    with open(os.path.join("data", "curve.json"), "r") as infile:
        data = json.load(infile)

    chain_id = str(chain["chain_id"])
    data[chain_id] = []

    provider = Contract.from_abi(
        "Curve Provider", "0x0000000022D53366457F9d5E68Ec105046FC4383", interface.CurveProvider.abi
    )
    registry = Contract.from_abi(
        "Curve Registry", provider.get_registry(), interface.CurveRegistry.abi
    )
    pool_info = Contract.from_explorer(provider.get_address(1))

    max_len = registry.pool_count()

    for i in range(max_len):
        address = registry.pool_list(i)

        pool_coins = pool_info.get_pool_coins(address).dict()
        underlying_coins = [
            coin.lower()
            for coin in pool_coins["underlying_coins"]
            if coin != "0x0000000000000000000000000000000000000000"
        ]
        name = registry.get_pool_name(address)
        asset_type = registry.get_pool_asset_type(address)

        object = {
            "name": name,
            "swap_address": address,
            "asset_type": asset_type,
            "coins": underlying_coins,
        }
        print(object)
        data[chain_id].append(object)
    with open(os.path.join("data", "curve.json"), "w") as outfile:
        json.dump(data, outfile, indent=2)
