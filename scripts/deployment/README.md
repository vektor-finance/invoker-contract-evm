# How to Use

Please first attempt a run locally before deploying to test/live network.

# Initial setup

You must first set up two EOAs `vektor_registry_deployer` and `vektor_trusted_deployer`.

The `vektor_registry_deployer` is the EOA which deploys the deployer contract. It is imperative that this account only performs one transaction, which is the transaction to deploy the deployer contract.

The `vektor_trusted_deployer` can be any account/address. In the long-term, we can/will transition this into a multi-sig. For now, we will use an EOA.

To create these, I would recommend typing:
`brownie accounts generate vektor_registry_deployer` and `brownie accounts generate vektor_trusted_deployer` which will generate the accounts locally in brownie, and password protect them.

You will receive the following output

```
SUCCESS: A new account '0xF2A749D98F5bF0A388978bd9397157c4f2B9D3ac' has been generated with the id 'vektor_registry_deployer'
SUCCESS: A new account '0xE983940c432D9e0a19B76496960583A83F112f39' has been generated with the id 'vektor_trusted_deployer'
```

You should then update the following lines in `scripts/deployment/__init__.py` to the new addresses:

```
REGISTRY_DEPLOYER = "0xFB47e88C3FFF913D48F8EB08DdD96f86338E2568"  # hardcoded
TRUSTED_DEPLOYER = "0x3302dBdD355fDfA7A439598885E189a4E9ad6B9b"  # hardcoded
```

## Deploying locally

Start hardhat by running `npx hardhat node`

In a new terminal window, type `brownie run deployment/registry --network hardhat`

This will prompt you for the password for the `vektor_registry_deployer`. After entering the password, it will deploy the CREATE2 deployer.

After deploying the CREATE2 Deployer, you can then deploy the rest of the contracts by typing `brownie run deployment/deploy --network hardhat`.

If you see a table that looks like this, then you have successfully deployed the contracts:

| network   | registry      | Invoker       | CMove            | CSwapUniswapV2   | CSwapUniswapV3   | CSwapCurve       |
|-----------|---------------|---------------|------------------|------------------|------------------|------------------|
| hardhat   | 0xFF8D...5511 | 0x62f2...8882 | ✅ 0x8ef5...9976 | ✅ 0xe3e8...13EA | ✅ 0xeCd0...0a38 | ✅ 0xb14a...fd18 |

## Deploying on testnets/live

### Fund Accounts

At the time of writing, 478,294 gas is required to deploy the CREATE2 deployer

To deploy CWrap, CSwapUniswapV2, CSwapUniswapV3, and CSwapCurve it will cost 4,815,396 gas. As we add further contracts, this number will increase.

To calculate the amount needed, take these values and insert them into this [calculator](https://legacy.ethgasstation.info/calculatorTxV.php) and add a buffer as necessary.
Example: 500,000 gas at 30 gwei will cost `0.015 eth`.
An 5,000,000 gas at 30 gwei will cost `0.15 eth`.

Therefore, transfer `0.015` ETH to the `vektor_registry_deployer`.
Also transfer `0.15` ETH to the `trusted_deployer`.

The same calculator can be used for other blockchains by taking the current gas price (eg 50 gwei on polygon) and replace the currency with the native currency.

### Deploy contracts

Repeat the steps described for local deployment, but replace the network flag with the network id (corresponding to `network-config.yaml`).

To deploy on rinkeby, you would type:
`brownie run deployment/registry --network ethereum-rinkeby-test`
`brownie run deployment/deploy --network ethereum-rinkeby-test`
