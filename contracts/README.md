# Contract Compatability

**TABLE OF CONTENTS**

- [Bridge](#bridge)
- [LP](#lp)
- [Move](#move)
    - [Supported Assets](#supported-asset-types)
    - [Compatability Issues](#known-compatability-issues)
- [Swap](#swap)
    - [Uniswap V2](#uniswap-v2)
    - [Curve](#curve)
    - [Uniswap V3](#uniswap-v3)

# Bridge

**UNSUPPORTED**

# LP

# Move

Allows assets to be transferred to/from the invoker.

For security purposes, we do not allow users to transfer assets directly between users. In order to transfer an asset between user `A` and user `B`, you must first transfer the asset from user `A` to the invoker and then transfer from the invoker to user `B`.

:bangbang: It is the responsibility of the calling function to ensure that assets which are transferred to the invoker are subsequently returned to the correct user within the same transaction. If this does not happen, the assets will be lost.

## Supported Asset types

- Native Token - This is the token used to pay for gas/network fees.
        
    Unsure compatibility for blockchain networks which utilise ERC20 tokens to pay for gas

- Standard ERC20 Token - This includes tokens which conform to [EIP-20](https://eips.ethereum.org/EIPS/eip-20). Note: some tokens do not follow the behaviour in an expected manner. These are listed below.
    - Non-confirming ERC20 tokens which do not return a `bool` on transfer/approval are supported. Tokens of this type include: USDT, OmiseGo, BNB(mainnet).

- Standard ERC721 Token (NFT) - This includes tokens which conform to [EIP-721](https://eips.ethereum.org/EIPS/eip-721).

## Known compatability issues

### ERC20
     
#### Deflationary / Fee-on-transfer tokens

These include tokens where the transferred amount and received amount are not identical. Any transfer using these tokens will revert. It is possible to enable this token class in the future. Possible causes could include:
    - Percentage of tokens transferred is burned (deflationary)
    - Percentage of tokens transferred is sent to a separate address (fee-on-transfer)

#### Rebasing / Elastic Supply tokens

There are many flavours of rebasing tokens, some of which are advertised as rebasing tokens (AMPL or OHM), others which are not immediately obvious (stETH). 
    
A standard ERC20 token uses a `mapping (address => uint256) balance`. Rebasing tokens instead issue a 'share' such that `share * shareMultiplier == balance`. Due to rounding errors, this causes the same issue with fee-on-transfer tokens.  
Consider the following example: 
    
> The current shareMultiplier ratio is `1.1`  
A user mints himself a balance of `100`. The contract performs `100/1.1` which issues the user with `90` shares (rounding is truncated).  
When attempting to transfer his `100` tokens, he actually only has a balance of `99` as `90` shares * `1.1` multipler  
Contract reverts

# Swap

Allows assets to be swapped for other assets. We define the following:
- SELL: The user specifies an exact amount of an input token
- BUY: The user specifies an exact amount of an output token

There is often a delay between transaction signing and transaction confirmation (minimum is the blocktime, however could be much longer depending on network conditions). It is therefore necessary to supply a `minAmountOut/maxAmountIn` parameter which indicates the threshold amount of the desired asset to be received/offered before the transaction reverts. This refers to different assets for SELL/BUY

## Uniswap V2

Note: "uniswap v2" refers to the venue type, rather than the venue itself.

### Supported pool types

All Uniswap V2 pools are compatible.

### Known compatibility issues

#### Imbalanced pools

Some Uniswap pools are `imbalanced` or `out-of-sync`. It is still possible to trade within these pools, however the price calculated by the OrderRouter for these pools may be different to the actual executed price. Transactions may therefore revert due to the slippage parameter. This occurs rarely, and is usually caused by one of the tokens within the pool having unexpected behaviour. These pools should be avoided.

## Curve

### Supported pool types

Curve pools that have been deployed by curve team are supported (ie. excluding factory pools).

### Known compatability issues

#### ETH pools

There are a few pools which utilise native ether and these are not currently supported.
These pools include:

| pool | assets | TVL
| --- | --- | --- |
| steth | ETH - stETH | $293.4m |
| seth | ETH - sETH | $18.6m |
| ankreth | ETH - ankrETH | $41,163 |
| reth | ETH - rETH | $3727 |

#### Factory Pools

A recent update to Curve has allowed for permisionless pool creation. These are called 'factory pools' and are demonstrated on the curve UI by the text `FACTORY`. At present, they are not supported.

## Uniswap V3

### Supported pools

All Uniswap V3 pools are supported. 

### Known compatability issues

No known issues

It is unknown whether there exists any compatibility issue with fee-on-transfer tokens as in uniswap v2. 
