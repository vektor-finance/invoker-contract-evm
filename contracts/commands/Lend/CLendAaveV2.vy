from vyper.interfaces import ERC20

LENDING_POOL: immutable(address)
REFERRAL_CODE: constant(uint16) = 0

interface LendingPool:
    def deposit(asset: address, amount: uint256, onBehalfOf: address, referralCode: uint16): nonpayable

@internal
def erc20_safe_approve(token: address, spender: address, amount: uint256):
    response: Bytes[32] = raw_call(
        token,
        concat(
            method_id("approve(address,uint256)"),
            convert(spender,bytes32),
            convert(amount,bytes32)
        ),
        max_outsize = 32
    )
    if len(response) > 0:
        assert convert(response,bool), "Approval failed"

@internal
def _approve_token(token: address, spender: address, amount: uint256):
    if ERC20(token).allowance(self, spender) > 0:
       self. erc20_safe_approve(token, spender, 0)
    self.erc20_safe_approve(token, spender, amount)


@external
def __init__(lending_pool: address):
    LENDING_POOL = lending_pool

@external
@payable
def deposit(asset: address, amount: uint256, receiver: address):
    self._approve_token(asset, LENDING_POOL, amount)
    LendingPool(LENDING_POOL).deposit(asset, amount, receiver, REFERRAL_CODE)
