from vyper.interfaces import ERC20

LENDING_POOL: immutable(address)
REFERRAL_CODE: constant(uint16) = 0

interface LendingPool:
    def deposit(asset: address, amount: uint256, onBehalfOf: address, referralCode: uint16): nonpayable
    def withdraw(asset: address, amount: uint256, to: address): nonpayable
    def borrow(asset: address, amount: uint256, interestRateMode: uint256, referralCode: uint16, onBehalfOf: address): nonpayable
    def repay(asset: address, amount: uint256, rateMode: uint256, onBehalfOf: address): nonpayable

interface aToken:
    def UNDERLYING_ASSET_ADDRESS() -> address: nonpayable

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
    """
    @dev design decision here whether we deploy one version of this contract to support all aave v2 forks vs only aave v2.
    If we choose to support all forks, `lending_pool` should instead be passed to each of the below functions.
    """
    LENDING_POOL = lending_pool

@external
@payable
def supply(asset: address, amount: uint256, receiver: address):
    """
    @notice supplies an asset to aave v2, receiving an aToken receipt
    @dev must first transfer asset to invoker
    @param asset the underlying asset
    @param amount the amount of asset to supply
    @param receiver the user to receive the aToken
    """
    self._approve_token(asset, LENDING_POOL, amount)
    LendingPool(LENDING_POOL).deposit(asset, amount, receiver, REFERRAL_CODE)

@external
@payable
def withdraw(a_asset: address, amount: uint256, receiver: address):
    """
    @notice withdraws supplied liquidity from aave v2
    @dev must first transfer aToken to invoker. user will receive 1:1
    @param a_asset the aToken
    @param amount the amount of a_token to withdraw. Can use type(uint).max to withdraw entire balance
    @param receiver the user to receive the underlying asset
    """
    underlying_asset: address = aToken(a_asset).UNDERLYING_ASSET_ADDRESS()
    self._approve_token(a_asset, LENDING_POOL, amount)
    LendingPool(LENDING_POOL).withdraw(underlying_asset, amount, receiver)

@external
@payable
def borrow(asset: address, amount: uint256, interest_rate_mode: uint256):
    """
    @notice borrow an asset from aave v2
    @dev user must first call approveDelegation() to allow invoker to generate debt
    @param asset the asset to borrow
    @param amount the amount of asset
    @param interest_rate_mode the desired interest rate mode. 1 = stable, 2 = variable
    """
    LendingPool(LENDING_POOL).borrow(asset, amount, interest_rate_mode, REFERRAL_CODE, msg.sender)

@external
@payable
def repay(asset: address, amount: uint256, interest_rate_mode: uint256): 
    """
    @notice repay a loan taken on aave v2
    @dev user must first transfer asset to invoker
    @param asset the underlying asset
    @param amount the amount of asset to repay
    @param interest_rate_mode the desired interest rate mode. 1 = stable, 2 = variable
    """
    self._approve_token(asset, LENDING_POOL, amount)
    LendingPool(LENDING_POOL).repay(asset, amount, interest_rate_mode, msg.sender)

# todo: makes sense to have a repayAll function
