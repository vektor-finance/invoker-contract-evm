# @version 0.3.7
"""
@title CLendCompoundV3.vy
@license Unlicensed
@notice This contract can be used by Invoker to interact with Compound V3

@dev compound v3 allows the invoker to be used without separate approvals.
We can either use supplyFrom (where the approval must be on the comet contract)
Alternatively, we can use supplyTo (where the approval must be on the invoker)

For a user only interacting with compound in one transaction, supplyFrom is better
However, for advanced features like collateral swap, we need to use supplyTo

To prototype, we will only support the basic case
"""

from vyper.interfaces import ERC20

interface Comet:
    def supplyFrom(from_: address, dst: address, asset: address, amount: uint256): nonpayable
    def withdrawFrom(from_: address, dst: address, asset: address, amount: uint256): nonpayable
    def supplyTo(dst: address, asset: address, amount: uint256): nonpayable
    def withdrawTo(to: address, asset: address, amount: uint256): nonpayable
    def transferAsset(dst: address, asset: address, amount: uint256): nonpayable
    def transferAssetFrom(src: address, dst: address, asset: address, amount: uint256): nonpayable

@internal
def _approve_token(token: address, spender: address, amount: uint256):
    if ERC20(token).allowance(self, spender) > 0:
       ERC20(token).approve(spender, 0, default_return_value=True)
    ERC20(token).approve(spender, amount, default_return_value=True)

# note: for all assets, it is possible to pass baseToken as the asset

@external
@payable
def transfer_asset_in(comet: address, asset: address, amount: uint256):
    """
    @dev User transfers collateral assets into Invoker
    User must have approved Invoker to interact with Comet
    """
    Comet(comet).transferAssetFrom(msg.sender, self, asset, amount)

@external
@payable
def transfer_asset_out(comet: address, asset: address, amount: uint256, receiver: address):
    """
    @dev User transfers collateral assets from Invoker
    """
    Comet(comet).transferAsset(receiver, asset, amount)

@external
@payable
def supply_user(comet: address, asset: address, amount: uint256, receiver: address):
    """
    @dev User supplies asset from their own address.
    User must have approved the Invoker to interact with that Comet
    """
    Comet(comet).supplyFrom(msg.sender, receiver, asset, amount)

@external
@payable
def supply_invoker(comet: address, asset: address, amount: uint256, receiver: address):
    """
    @dev User supplies asset from Invoker
    """
    self._approve_token(asset, comet, amount)
    Comet(comet).supplyTo(receiver, asset, amount)

@external
@payable
def withdraw_user(comet: address, asset: address, amount: uint256, receiver: address):
    """
    @dev User withdraws asset whilst collateral is in their address
    """
    # Operator: Invoker
    # src: user
    # to: receiver
    Comet(comet).withdrawFrom(msg.sender, receiver, asset, amount)

@external
@payable
def withdraw_invoker(comet: address, asset: address, amount: uint256, receiver: address):
    """
    @dev User withdraws asset whilst collateral is in Invoker
    """
    # operator: Invoker
    # src: Invoker
    # to: receiver
    Comet(comet).withdrawTo(receiver, asset, amount)
