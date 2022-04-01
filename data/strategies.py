from typing import Any, Callable, Optional

from brownie import ZERO_ADDRESS, network
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from hypothesis.strategies._internal.deferred import DeferredStrategy

from data.chain import get_chain
from data.uniswapv3 import UniswapV3FeeAmount


class _DeferredStrategyRepr(DeferredStrategy):
    def __init__(self, fn: Callable, repr_target: str) -> None:
        super().__init__(fn)
        self._repr_target = repr_target

    def __repr__(self):
        return f"sampled_from({self._repr_target})"


def _uniswapv3_fee_strategy() -> SearchStrategy:
    return _DeferredStrategyRepr(
        lambda: st.sampled_from(UniswapV3FeeAmount.list()), "Uniswap V3 FeeAmount"
    )


def token_strategy() -> SearchStrategy:
    chain = get_chain()
    tokens = [asset for asset in chain["assets"] if asset.get("address")]

    return _DeferredStrategyRepr(lambda: st.sampled_from(tokens), "ERC20 token")


def receiver_strategy(length: Optional[int] = None) -> SearchStrategy:
    return _DeferredStrategyRepr(
        lambda: st.sampled_from([*list(network.accounts)[:length], ZERO_ADDRESS]), "accounts"
    )


def integration_strategy(type_str, **kwargs: Any) -> SearchStrategy:
    if type_str == "uniswapv3_fee":
        return _uniswapv3_fee_strategy(**kwargs)

    raise ValueError(f"No strategy available for type: {type_str}")
