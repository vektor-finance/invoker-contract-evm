import json

import requests
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

    CHAIN_ID = chain["chain_id"]
    r = requests.get(
        f"https://bridgeapi.anyswap.exchange/v3/serverinfoV3?chainId={CHAIN_ID}&version=all"
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
                        print(json.dumps(parsed, indent=1))

    r = requests.get(
        f"https://bridgeapi.anyswap.exchange/v3/serverinfoV4?chainId={CHAIN_ID}&version=all"
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
                        print(json.dumps(parsed, indent=1))


"""
Running 'scripts/get_any_token.py::main'...

---V3 API---
{
 "underlyingName": "USDCoin",
 "underlyingAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "anyAddress": "0x7ea2be2df7ba6e54b1a9c70676f668455e329d29",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "66",
  "137",
  "250",
  "42161",
  "43114"
 ]
}
{
 "underlyingName": "DaiStablecoin",
 "underlyingAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "anyAddress": "0x739ca6d71365a08f584c8fc4e1029045fa8abc4b",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "137",
  "250",
  "43114"
 ]
}
{
 "underlyingName": "TetherUSD",
 "underlyingAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "anyAddress": "0x22648c12acd87912ea1710357b1302c6a4154ebc",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "66",
  "128",
  "137",
  "250",
  "43114"
 ]
}
{
 "underlyingName": "WrappedBTC",
 "underlyingAddress": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
 "anyAddress": "0xe6b9d092223f39013656702a40dbe6b7decc5746",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "66",
  "128",
  "137",
  "250",
  "43114"
 ]
}
{
 "underlyingName": "DaiStablecoin",
 "underlyingAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "anyAddress": "0x639a647fbe20b6c8ac19e48e2de44ea792c62c5c",
 "router": "0x765277eebeca2e31912c9946eae1021199b39c61",
 "destChains": [
  "56"
 ]
}
---V4 API---
{
 "underlyingName": "USDCoin",
 "underlyingAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "anyAddress": "0x7ea2be2df7ba6e54b1a9c70676f668455e329d29",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "66",
  "137",
  "250",
  "42161",
  "43114"
 ]
}
{
 "underlyingName": "DaiStablecoin",
 "underlyingAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "anyAddress": "0x739ca6d71365a08f584c8fc4e1029045fa8abc4b",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "137",
  "250",
  "43114"
 ]
}
{
 "underlyingName": "TetherUSD",
 "underlyingAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "anyAddress": "0x22648c12acd87912ea1710357b1302c6a4154ebc",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "66",
  "128",
  "137",
  "250",
  "43114"
 ]
}
{
 "underlyingName": "WrappedBTC",
 "underlyingAddress": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
 "anyAddress": "0xe6b9d092223f39013656702a40dbe6b7decc5746",
 "router": "0x6b7a87899490ece95443e979ca9485cbe7e71522",
 "destChains": [
  "56",
  "66",
  "128",
  "137",
  "250",
  "43114"
 ]
}
{
 "underlyingName": "DaiStablecoin",
 "underlyingAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "anyAddress": "0x639a647fbe20b6c8ac19e48e2de44ea792c62c5c",
 "router": "0x765277eebeca2e31912c9946eae1021199b39c61",
 "destChains": [
  "56"
 ]
}
"""
