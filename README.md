# invoker-contract-evm

[![main](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/main.yaml/badge.svg)](https://github.com/vektor-finance/invoker-contract-evm/actions/workflows/main.yaml)

## Getting Started

### Environment Variables

This project requires you have an API key for:

- [Etherscan](https://etherscan.io/apis)
- [Infura](https://infura.io/)

Both are free to create.

### Creating a Virtual Environment and installing Python dependencies

It is **strongly recommended** use a virtual environment with this project. This ensures that dependencies are strictly contained within your project and will not alter or affect your other development environment.

To create a new virtual environment and install the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

In future sessions, activate the virtual environment with:

```bash
source venv/bin/activate
```

To learn more about `venv`, see the official [Python documentation](https://docs.python.org/3/library/venv.html).

To add convenience commands you can check out [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).

### Installing Hardhat

This project uses [Hardhat](https://hardhat.org/) to fork the blockchain for testing.

```bash
yarn install
```

### Configuring Pre-commit

[Pre-commit](https://pre-commit.com/) is a tool that executes linting checks each time you make a commit. It is useful for enforcing proper codestyle and preventing commits that would fail the linting build.

To install pre-commit locally:

```bash
pre-commit install
```

Once installed, the pre-commit hooks will automatically run each time you make a commit.

You can also run them ad-hoc with:

```bash
pre-commit run --all-files
```

## Running the Tests

This project uses [tox](https://tox.readthedocs.io/en/latest/) to standardize the local and remote testing environments.

To run all of your project's unit tests and perform linting checks:

```bash
tox
```

To run only the linting checks:

```bash
tox -e lint
```

To run only brownie tests:

```bash
brownie test
```
