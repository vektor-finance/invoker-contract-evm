"""
@title CLendAave.vy
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
    def baseToken() -> address: nonpayable

@external
@payable
def supply(comet: address, asset: address, amount: uint256, receiver: address):
    """
    @dev User does not need to approve invoker to spend their assets, 
    however user must call Comet.allow(Invoker, True)
    """
    Comet(comet).supplyFrom(msg.sender, receiver, asset, amount)

@external
@payable
def withdraw(comet: address, asset: address, amount: uint256, receiver: address):
    Comet(comet).withdrawFrom(msg.sender, receiver, asset, amount)

@external
@payable
def borrow(comet: address, amount: uint256, receiver: address):
    base_asset: address = Comet(comet).baseToken()
    Comet(comet).withdrawFrom(msg.sender, receiver, base_asset, amount)

@external
@payable
def repay(comet: address, amount: uint256, receiver: address):
    base_asset: address = Comet(comet).baseToken()
    Comet(comet).supplyFrom(msg.sender, receiver, base_asset, amount)
