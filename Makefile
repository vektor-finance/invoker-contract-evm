.PHONY: test-all

NETWORKS = hardhat \
mainnet-hardhat-fork rinkeby-hardhat-fork \
polygon-hardhat-fork mumbai-hardhat-fork \
fantom-hardhat-fork \
arbitrum-hardhat-fork \
avalanche-hardhat-fork \
bsc-hardhat-fork

test-all:
	for network in ${NETWORKS}; do \
		echo "Testing $$network"; \
		brownie test --network $$network; \
	done

get-all-curve:
	for network in ${NETWORKS}; do \
		echo "Getting Curve pools for $$network"; \
		brownie run get_curve.py --network $$network; \
	done
