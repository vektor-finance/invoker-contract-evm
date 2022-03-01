from dataclasses import dataclass
from typing import List

CURVE_ASSET_TYPE_USD = 0
CURVE_ASSET_TYPE_BTC = 1
CURVE_ASSET_TYPE_ETH = 2
CURVE_ASSET_TYPE_STABLE = 3
CURVE_ASSET_TYPE_CRYPTO = 4


@dataclass
class CurvePool:
    name: str
    swap_address: str
    asset_type: int
    coins: List[str]


CURVE_POOLS = {
    "1": [
        CurvePool(
            "3pool",
            "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7",
            CURVE_ASSET_TYPE_USD,
            [
                "0x6b175474e89094c44da98b954eedeac495271d0f",
                "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            ],
        ),
        CurvePool(
            "tricrypto",
            "0xd51a44d3fae010294c616388b506acda1bfaae46",
            CURVE_ASSET_TYPE_CRYPTO,
            [
                "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
                "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            ],
        ),
    ]
}


def get_curve_pools(chain_id: str):
    chain_id = str(chain_id)
    return CURVE_POOLS.get(chain_id)


def get_curve_complement(chain_id: str, coin: str):
    chain_id = str(chain_id)
    for pool in CURVE_POOLS.get(chain_id):
        if coin in pool.coins:
            complement = pool.coins.copy()
            complement.remove(coin)
            return pool.swap_address, complement
    return None, None
