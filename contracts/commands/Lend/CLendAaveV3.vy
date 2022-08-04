from vyper.interfaces import ERC20

LENDING_POOL: immutable(address)
REFERRAL_CODE: constant(uint16) = 0

interface Pool:
    def supply(asset: address, amount: uint256, onBehalfOf: address, referralCode: uint16): nonpayable
    def withdraw(asset: address, amount: uint256, to: address): nonpayable
    def borrow(asset: address, amount: uint256, interestRateMode: uint256, referralCode: uint16, onBehalfOf: address): nonpayable
    def repay(asset: address, amount: uint256, rateMode: uint256, onBehalfOf: address): nonpayable

interface aToken:
    def UNDERLYING_ASSET_ADDRESS() -> address: nonpayable

# can use default_return_value in vyper 0.3.4
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
       self.erc20_safe_approve(token, spender, 0)
    self.erc20_safe_approve(token, spender, amount)

@external
def __init__(lending_pool: address):
    LENDING_POOL = lending_pool
    
@payable
@external
def supply(asset: address, amount: uint256, receiver: address):
    self._approve_token(asset, LENDING_POOL, amount)
    Pool(LENDING_POOL).supply(asset, amount, receiver, REFERRAL_CODE)

@external
@payable
def withdraw(a_asset: address, amount: uint256, receiver: address):
    underlying_asset: address = aToken(a_asset).UNDERLYING_ASSET_ADDRESS()
    self._approve_token(a_asset, LENDING_POOL, amount)
    Pool(LENDING_POOL).withdraw(underlying_asset, amount, receiver)

@external
@payable
def borrow(asset: address, amount: uint256, interest_rate_mode: uint256):
    Pool(LENDING_POOL).borrow(asset, amount, interest_rate_mode, REFERRAL_CODE, msg.sender)

@external
@payable
def repay(asset: address, amount: uint256, interest_rate_mode: uint256): 
    self._approve_token(asset, LENDING_POOL, amount)
    Pool(LENDING_POOL).repay(asset, amount, interest_rate_mode, msg.sender)
