# tests

Tests scripts.

## Rationale

In order to support deployment across multiple chains with differing protocols and assets, we must have a robust testing strategy.

- Tests within `core` will test the core functionality of the invoker and any 'Command' contract.
'core' tests will be performed against a development network. They must not interact with any pre-existing contracts that are already deployed. These tests will utilise mock tockens

- Tests within `integration` will be performed against all chains, protocols and assets supported by the `*.yaml` files in the data subdirectory from the root directory of this project.
'integration' tests are performed against many networks. They can be used to establish whether there are any unexpected ABI/token incompatabilities before we deploy on a network. (For example, trader joe using a separate ABI to the standard uniswap router)

- Tests within `combination` are performed only against the specified chain. They are used to test more complicated use-cases of the invoker in a way that would not be possible for us to test using unit-tests.
Examples of this may include MOVE.SPLIT(). The intention of these tests is to test more complicated invocations.
