import requests
from brownie import network

from data.chain import get_chain_from_network_name


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
    data = r.json()

    tokens = [asset for asset in chain["assets"] if asset.get("address")]

    for type in data:
        for addr, token in data[type].items():
            # there are tokens where underlying is 'False'
            if isinstance(token["underlying"], dict):

                # Filter over the tokens we are interested in
                for chain_token in tokens:
                    if token["underlying"]["address"] == chain_token.get("address"):

                        print(token["underlying"]["name"])
                        print("Underlying: ", token["underlying"]["address"])
                        print("anyTOKEN:", token["anyToken"]["address"])
                        print("Router: ", token["router"])
                        print("Dest Chains: ", list(token["destChains"].keys()))
                        print("")


"""
Running 'scripts/get_any_token.py::main'...

USDCoin
Underlying:  0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
anyTOKEN: 0x7ea2be2df7ba6e54b1a9c70676f668455e329d29
Router:  0x6b7a87899490ece95443e979ca9485cbe7e71522
Dest Chains:  ['56', '66', '137', '250', '42161', '43114']

DaiStablecoin
Underlying:  0x6b175474e89094c44da98b954eedeac495271d0f
anyTOKEN: 0x739ca6d71365a08f584c8fc4e1029045fa8abc4b
Router:  0x6b7a87899490ece95443e979ca9485cbe7e71522
Dest Chains:  ['56', '137', '250', '43114']

TetherUSD
Underlying:  0xdac17f958d2ee523a2206206994597c13d831ec7
anyTOKEN: 0x22648c12acd87912ea1710357b1302c6a4154ebc
Router:  0x6b7a87899490ece95443e979ca9485cbe7e71522
Dest Chains:  ['56', '66', '128', '137', '250', '43114']

WrappedBTC
Underlying:  0x2260fac5e5542a773aa44fbcfedf7c193bc2c599
anyTOKEN: 0xe6b9d092223f39013656702a40dbe6b7decc5746
Router:  0x6b7a87899490ece95443e979ca9485cbe7e71522
Dest Chains:  ['56', '66', '128', '137', '250', '43114']

DaiStablecoin
Underlying:  0x6b175474e89094c44da98b954eedeac495271d0f
anyTOKEN: 0x639a647fbe20b6c8ac19e48e2de44ea792c62c5c
Router:  0x765277eebeca2e31912c9946eae1021199b39c61
Dest Chains:  ['56']
"""
