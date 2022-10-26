# @version 0.3.7
"""
Simple ERC20 contract which can be used for testing.
DO NOT deploy this
Implementation is designed to mimic tokens such as StETH/aTokens/AMPL/sOHM
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

shares: HashMap[address, uint256]
allowance: public(HashMap[address, HashMap[address, uint256]])
total_pooled_ether: uint256
total_shares: uint256

@external
@view
def totalSupply() -> uint256:
    return self.total_pooled_ether

@external
@view
def balanceOf(account: address) -> uint256:
    if self.total_shares == 0:
        return 0
    else:
        return self.shares[account] * self.total_pooled_ether / self.total_shares

@external
def __init__(_name: String[64], _symbol: String[32], _decimals: uint8):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals

@internal
@view
def _get_shares_by_eth(amount: uint256) -> uint256:
    if self.total_pooled_ether == 0:
        return 0
    else:
        return amount * self.total_shares / self.total_pooled_ether


@external
def transfer(_to : address, _value : uint256) -> bool:
    _amount: uint256 = self._get_shares_by_eth(_value)
    self.shares[msg.sender] -= _amount
    self.shares[_to] += _amount
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    _amount: uint256 = self._get_shares_by_eth(_value)
    self.shares[_from] -= _amount
    self.shares[_to] += _amount
    self.allowance[_from][msg.sender] -= _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def set_pooled_eth(amount: uint256):
    "debug function"
    self.total_pooled_ether = amount

@external
def mint(_to: address, _shares: uint256):
    # this function is only being used for testing
    self.total_shares += _shares
    self.shares[_to] += _shares
