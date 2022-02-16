import os

import yaml


def _get_anyswap_data():
    with open(os.path.join("data", "anyswap.yaml"), "r") as file:
        return yaml.safe_load(file)


def get_anyswap_tokens_for_chain(chain_id):
    data = _get_anyswap_data()
    chain_id = str(chain_id)

    return data.get(chain_id)
