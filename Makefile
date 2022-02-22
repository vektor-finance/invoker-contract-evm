.PHONY: test-all

NETWORKS=hardhat mainnet-hardhat-fork rinkeby-hardhat-fork polygon-hardhat-fork mumbai-hardhat-fork fantom-hardhat-fork arbitrum-hardhat-fork avalanche-hardhat-fork

test-all:
	for network in ${NETWORKS}; do \
		echo "Testing $$network"; \
		brownie test --network $$network; \
	done
