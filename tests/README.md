# vektor-finance/invoker-contract-evm/tests

Tests scripts.

## Rationale

In order to support deployment across multiple chains with differing protocols and assets, we must have a robust testing strategy.

- Tests within `core` will test the core functionality of the invoker and any 'Command' contract.
It is expected that these tests will be performed against a pure 'dev' network
- Tests within `integrations` will be performed against all chains, protocols and assets supported by the `*.yaml` files in the data subdirectory from the root directory of this project.