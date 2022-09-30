# @version 0.3.7
"""
Simple ERC20 contract which can be used for testing.
Sends 5% of transferred amount to owner, and burns 5%
DO NOT deploy this
"""

from vyper.interfaces import ERC20
from vyper.interfaces import ERC20Detailed

implements: ERC20
implements: ERC20Detailed

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

name: public(String[64])
symbol: public(String[32])
decimals: public(uint8)

balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])
totalSupply: public(uint256)

owner: public(address)


@external
def __init__(_name: String[64], _symbol: String[32], _decimals: uint8):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.owner = msg.sender


@external
def transfer(_to : address, _value : uint256) -> bool:
    fee: uint256 = _value/20
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value - 2*fee
    self.balanceOf[self.owner] += fee
    log Transfer(msg.sender, _to, _value-2*fee)
    log Transfer(msg.sender, self.owner, fee)
    log Transfer(msg.sender, ZERO_ADDRESS, fee)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    fee: uint256 = _value/20
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value - 2*fee
    self.balanceOf[self.owner] += fee
    self.allowance[_from][msg.sender] -= _value
    log Transfer(_from, _to, _value-2*fee)
    log Transfer(_from, self.owner, fee)
    log Transfer(_from, ZERO_ADDRESS, fee)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def mint(_to: address, _value: uint256):
    # this function is only being used for testing
    self.totalSupply += _value
    self.balanceOf[_to] += _value
    log Transfer(ZERO_ADDRESS, _to, _value)
