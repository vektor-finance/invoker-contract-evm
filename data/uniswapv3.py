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
