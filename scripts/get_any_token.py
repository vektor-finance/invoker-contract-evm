import requests
import yaml
from brownie import network

from data.chain import get_chain_from_network_name


def _parse_v3_dict(token):
    return {
        "underlyingName": token["underlying"]["name"],
        "underlyingAddress": token["underlying"]["address"],
        "anyAddress": token["anyToken"]["address"],
        "router": token["router"],
        "destChains": list(token["destChains"].keys()),
    }


def _parse_v4_dict(token):
    return {
        "underlyingName": token["name"],
        "underlyingAddress": token["address"],
        "anyAddress": token["underlying"]["address"],  # note: anyToken is underlying in v4
        "router": token["routerToken"],
        "destChains": list(token["destChains"].keys()),
    }


def main():

    (chain, _) = get_chain_from_network_name(network.show_active())
    if not chain:
        raise ValueError(
            "Network not supported in config. Please review data/chains.yaml", network.show_active()
        )

    chain_id = chain["chain_id"]
    r = requests.get(
        f"https://bridgeapi.anyswap.exchange/v3/serverinfoV3?chainId={chain_id}&version=all"
    )
    v3_data = r.json()

    tokens = [asset for asset in chain["assets"] if asset.get("address")]

    # Get data from V3 api

    print("---V3 API---")
    for type in v3_data:
        for addr, token in v3_data[type].items():
            # there are tokens where underlying is 'False'
            if isinstance(token["underlying"], dict):

                parsed = _parse_v3_dict(token)

                # Filter over the tokens we are interested in
                for chain_token in tokens:
                    if parsed["underlyingAddress"] == chain_token.get("address"):
                        print(yaml.dump(parsed))

    r = requests.get(
        f"https://bridgeapi.anyswap.exchange/v3/serverinfoV4?chainId={chain_id}&version=all"
    )
    v4_data = r.json()

    print("---V4 API---")
    for type in v4_data:
        for addr, token in v4_data[type].items():

            if isinstance(token["underlying"], dict):

                parsed = _parse_v4_dict(token)

                # Filter over the tokens we are interested in
                for chain_token in tokens:
                    if parsed["underlyingAddress"] == chain_token.get("address"):
                        print(yaml.dump(parsed))
