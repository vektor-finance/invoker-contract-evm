# invoker-contract-evm

[![lint](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/lint.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/lint.yaml)
[![docker](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/docker.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/docker.yaml)
[![core](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/core.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/core.yaml)
[![integration](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/integration.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/integration.yaml)

Solidity contracts for Vektor's EVM invoker.

- [Overview](#overview)
- [Testing and Development](#testing-and-development)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
  - [GPG Key](#create-and-setup-gpg-key-on-macos)
  - [Git-crypt](#setup-git-encrypt)
  - [Configuring Pre-Commit](#configuring-pre-commit)
  - [Running The Tests](#running-the-tests)
- [Integration Testing](#integration-testing)
  - [Adding new blockchains](#adding-new-blockchains)
- [Scripts](#scripts)
  - [Faucet](#faucet)

## Overview

TODO

## Deployments

| registry                                   | Invoker                                    | CMove                                      | CWrap                                      | CSwapUniswapV2                             | CSwapUniswapV3                             | CSwapCurve                                 |
|--------------------------------------------|--------------------------------------------|--------------------------------------------|--------------------------------------------|--------------------------------------------|--------------------------------------------|--------------------------------------------|
| 0xEcDFb7e848a9Ce0AE9c5dBEB5F9Ed10a8A5E2635 | 0xA7dAC6938b17c4ac0BF879F4Bf8d2020c2c1EdB1 | 0x1d868fD27f92a490142F1Fc8583104573CE8f191 | 0xC2cA82f0A8E904C648E85b1ebbC92051Fb53399e | 0x68DF154F0ac49f7eD1A4CbDf6c5Fa70DB2Cb91Fb | 0x7DC7274c3b27542685fb093582955ABCf57987f4 | 0xf004CbD67d02166157f30A8085c69842ad556b24 |
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

### Create and Setup GPG key on macOS

1. Install `gnugpg` and `pinentry-mac` - `brew install gnupg pinentry-mac`
2. Generate a GPG key - `gpg --full-generate-key`. Use defaults, your `@vektor.finance` email and add a passphrase
3. Get the key id by using - `gpg --list-secret-keys --keyid-format=long`. It's the value after the encryption format e.g. `sec ed25519/<key-id>`
4. Configure git with the GPG key - `git config --global user.signingkey <key-id>`
5. Add the GPG key to GitHub [here](https://github.com/settings/gpg/new) - `gpg --armor --export <key-id> | pbcopy`
6. Open the file `~/.gnupg/gpg-agent.conf` and add `pinentry-program /opt/homebrew/bin/pinentry-mac`
7. Tell `git` to use your GPG key for all signing going forward `git config --global commit.gpgsign true`

Some other useful steps for debugging can be found [here](https://gist.github.com/troyfontaine/18c9146295168ee9ca2b30c00bd1b41e)

### Setup git-encrypt

1. Install [git-encrypt](https://github.com/AGWA/git-crypt/blob/master/INSTALL.md) - `brew install git-crypt`
2. Ensure your `GPG` Key identifier is added - e.g. key ID, a full fingerprint, an email address - speak to @akramhussein
3. Once your `GPG` key has been added to the repo, you can pull the latest repo and run `git-crypt unlock`

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
