# invoker-contract-evm [archived]

`THIS REPOSITORY IS NOT IN USE OR UNDER DEVELOPMENT`

[![lint](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/lint.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/lint.yaml)
[![core](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/core.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/core.yaml)
[![integration](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/integration.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/integration.yaml)

Solidity contracts for Vektor's EVM invoker.

- [Overview](#overview)
- [Testing and Development](#testing-and-development)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
  - [Configuring Pre-Commit](#configuring-pre-commit)
  - [Running The Tests](#running-the-tests)
- [Integration Testing](#integration-testing)
  - [Adding new blockchains](#adding-new-blockchains)
- [Scripts](#scripts)
  - [Faucet](#faucet)

## Overview

Vektor's EVM Invoker contracts

## Deployments

Contracts are deployed to the same addresses on all chains.

| name            | address                                       |
|-----------------|-----------------------------------------------|
| Invoker         | 0x805337bC5195f2BfEa531665eDa46516fa493949    |
| CMove           | 0x03E64b667B0DDdABb2972dF49C318E96D414E87f    |
| CWrap           | 0xC2cA82f0A8E904C648E85b1ebbC92051Fb53399e    |
| CSwapUniswapV2  | 0x094FcB456687382c836aD61c46DcEcC3C2b88911    |
| CSwapUniswapV3  | 0x8b9cE67DC4367EbC13025cA352277b2b4A1B30Ee    |
| CSwapCurve      | 0x6C7Cd683949Dcd5A39486390c7F7C59a55309ce1    |
| CLendAave       | 0x565562e7CFF1c10F5Fa1D2F67Eb17F92b846b490    |
| CLendCompoundV3 | 0xf9783c52C250b4bDBE2F4B0bc5A9a424569e5794    |
| CLPUniswapV2    | 0x17e21Cfb1c7B2E6f6740D675e565809D357E38E9    |
| CLPUniswapV3    | 0xfABEC98dBaB8A86Bee8413A45c89204CcB8bc865    |
| CLPCurve        | 0x91fb92d0c69F0EbBab584F9Fc38177F79711b705    |

## Chains

- Ethereum
- Polygon
- Arbitrum
- Optimism
- Gnosis
- BNBChain
- Fantom
- Avalanche
- Moonbeam
- Moonriver

## Testing and Development

### Dependencies

- [python3](https://www.python.org/downloads/release/python/) - tested with version `3.8.6`.
- [brownie](https://github.com/iamdefinitelyahuman/brownie) - tested with version `1.16.0`.
- [hardhat](https://hardhat.org/) - tested with version `2.6.0`.

### Setup

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html).

Next, clone the repo and install the developer dependencies:

```bash
git clone https://github.com/vektor-finance/invoker-contract-evm.git
cd invoker-contract-evm
pip install -r requirements.txt -r requirements.dev.txt
yarn install
```

### Configuring Pre-commit

[Pre-commit](https://pre-commit.com/) is a tool that executes linting checks each time you make a commit.

It is useful for enforcing proper codestyle and preventing commits that would fail the linting build.

To install pre-commit locally:

```bash
pre-commit install
```

Once installed, the pre-commit hooks will automatically run each time you make a commit.

You can also run them ad-hoc with:

```bash
pre-commit run --all-files
```

### Running the Tests

To run the entire suite:

```bash
brownie test
```

## Integration Testing

### Adding new Blockchains

In order to add a new blockchain to the testing suite, perform the following:

1. Create an entry in `data/chains.yaml` with the relevant contract addresses.
Many of the fields are self-explanatory, however please note:
    - The `network` field refers to the name of the network in the brownie config. We distinguish between a 'prod' network (which is the real network, and will be used for any deployments) and a 'fork' network (which will be a hardhat fork, used for all the testing).
    - EIP1559 status is specified by a flag (It is possible to disable 1559, even when a network supports it)
    - For each asset, please enter the name, symbol and decimals as directed by the smart contract. Please lowercase the address (for consistency)
    - The `benefactor` is an address that contains a large sum of the relevant token. (The testing suite moves tokens from the benefactor to the test users). For the purposes of these tests, it is best to pick a smart contract benefactor that we are unlikely to interact with (a yearn/aave vault is a good example)
2. Update `network-config.yaml` in root directory with the relevant information. You will likely need to create two entries. One for the 'prod' network, and one for the 'fork' network
3. Update the CI and Makefile to include the network name (only the fork).
4. Ensure any private RPC url are located within encrypted .env file.
5. Add the RPC url to GitHub Secrets and import in the `env` block of the [CI workflow](.github/workflows/main.yaml).

## Scripts

Brownie scripts can be called with `brownie run <script-name>`

### Faucet

The `faucet` script swaps `ETH` for a selection of `ERC20` tokens that are defined in `scripts/addresses.py`.

**Usage:** `brownie run faucet`

**Arguments:**

Prefix the `key=value` before calling the command e.g. `ACCOUNT=2 ETH=1.5 brownie run faucet`

- `ACCOUNT` - account index (e.g. 12) or address `0x....` to use. Defaults to account index 0.
- `ETH` - ETH to use per swap. Defaults to 0.5 ETH.
