import requests

# def _get_anyswap_data():
#     with open(os.path.join("data", "anyswap.yaml"), "r") as file:
#         return yaml.safe_load(file)


# def get_anyswap_tokens_for_chain(chain_id):
#     data = _get_anyswap_data()
#     chain_id = str(chain_id)

#     return data.get(chain_id).get("assets")


# def get_anyswap_native_for_chain(chain_id):
#     data = _get_anyswap_data()
#     chain_id = str(chain_id)

#     return data.get(chain_id).get("anyNative")


def _parse_v3_dict(token):
    return {
        "underlyingName": token["underlying"]["name"],
        "underlyingAddress": token["underlying"]["address"],
        "anyAddress": token["anyToken"]["address"],
        "router": token["router"],
        "destChains": list(token["destChains"].keys()),
    }


def get_anyswap_tokens_for_chain(chain):

    chain_id = str(chain["chain_id"])
    r = requests.get(
        f"https://bridgeapi.anyswap.exchange/v3/serverinfoV3?chainId={chain_id}&version=all"
    )
    v3_data = r.json()

    tokens = [asset for asset in chain["assets"] if asset.get("address")]

    output = {chain_id: {"assets": []}}

    # Get data from V3 api

    for type in v3_data:
        for _, token in v3_data[type].items():
            # there are tokens where underlying is 'False'
            if isinstance(token["underlying"], dict):

                parsed = _parse_v3_dict(token)

                # Filter over the tokens we are interested in
                for chain_token in tokens:
                    if parsed["underlyingAddress"] == chain_token.get("address"):
                        output[chain_id]["assets"].append(parsed)

    return output
