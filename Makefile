.PHONY: test-all

NETWORKS = hardhat \
mainnet-hardhat-fork ethereum-rinkeby-hardhat-fork \
polygon-hardhat-fork polygon-mumbai-hardhat-fork \
fantom-hardhat-fork \
arbitrum-hardhat-fork \
avalanche-hardhat-fork \
bsc-hardhat-fork \
optimism-hardhat-fork \ 
optimism-kovan-hardhat

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
