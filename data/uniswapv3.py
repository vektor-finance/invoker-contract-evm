import math
from enum import IntEnum


class UniswapV3FeeAmount(IntEnum):
    """
    Fee provided to the UniswapV3 liquidity providers.
    Denominated in BIPS.
    """

    VERY_LOW = 100
    LOW = 500
    MEDIUM = 3000
    HIGH = 10000

    @staticmethod
    def list():
        return list(map(lambda c: c.value, UniswapV3FeeAmount))

    @staticmethod
    def labels():
        return list(map(lambda c: "FEE_" + c.name, UniswapV3FeeAmount))


Q96 = 0x1000000000000000000000000
RESOLUTION = 96


def get_sqrt_ratio_at_tick(tick):
    return math.sqrt(1.0001**tick) * Q96


def get_liquidity_for_amount0(sqrt_ratioA, sqrt_ratioB, amount0):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)
    intermediate = sqrt_ratioA * sqrt_ratioB / Q96
    return int(amount0 * intermediate / (sqrt_ratioB - sqrt_ratioA))


def get_liquidity_for_amount1(sqrt_ratioA, sqrt_ratioB, amount1):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)
    return int(amount1 * Q96 / (sqrt_ratioB - sqrt_ratioA))


def get_liquidity_for_amounts(sqrt_ratio, sqrt_ratioA, sqrt_ratioB, amount0, amount1):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)

    if sqrt_ratio <= sqrt_ratioA:
        liquidity = get_liquidity_for_amount0(sqrt_ratioA, sqrt_ratioB, amount0)
    elif sqrt_ratio < sqrt_ratioB:
        liquidity0 = get_liquidity_for_amount0(sqrt_ratio, sqrt_ratioB, amount0)
        liquidity1 = get_liquidity_for_amount1(sqrt_ratioA, sqrt_ratio, amount1)
        liquidity = liquidity0 if liquidity0 < liquidity1 else liquidity1
    else:
        liquidity = get_liquidity_for_amount1(sqrt_ratioA, sqrt_ratioB, amount1)

    return liquidity


def get_amount0_for_liquidity(sqrt_ratioA, sqrt_ratioB, liquidity):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)
    return int(
        ((liquidity << RESOLUTION) * (sqrt_ratioB - sqrt_ratioA) / sqrt_ratioB) / sqrt_ratioA
    )


def get_amount1_for_liquidity(sqrt_ratioA, sqrt_ratioB, liquidity):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)
    return int(liquidity * (sqrt_ratioB - sqrt_ratioA) / Q96)


def get_amounts_for_liquidity(sqrt_ratio, sqrt_ratioA, sqrt_ratioB, liquidity):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)

    amount0, amount1 = (0, 0)

    if sqrt_ratio <= sqrt_ratioA:
        amount0 = get_amount0_for_liquidity(sqrt_ratioA, sqrt_ratioB, liquidity)
    elif sqrt_ratio < sqrt_ratioB:
        amount0 = get_amount0_for_liquidity(sqrt_ratio, sqrt_ratioB, liquidity)
        amount1 = get_amount1_for_liquidity(sqrt_ratioA, sqrt_ratio, liquidity)
    else:
        amount1 = get_amount1_for_liquidity(sqrt_ratioA, sqrt_ratioB, liquidity)

    return (amount0, amount1)
