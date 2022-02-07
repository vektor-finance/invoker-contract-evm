def get_weth_address(chain):
    """Get the first WETH address from chain
    Does this by checking for wrapped_native
    If multiple assets exists, it returns the first
    """

    def generator(chain):
        tokens = chain["assets"]
        for token in tokens:
            if token.get("wrapped_native"):
                yield token

    return next(generator(chain))["address"]


def get_uni_router_address(chain):
    """Get the first uniswap router
    Does this by checking interfaces
    If multiple routers exist, it returns the first
    """

    def generator(chain):
        contracts = chain["contracts"]
        for contract in contracts:
            if "uniswap_router_v2_02" in contract["interfaces"]:
                yield contract

    return next(generator(chain))["address"]
