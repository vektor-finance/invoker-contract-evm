from eth_utils import keccak, to_checksum_address
from rlp import encode


def get_create1_address(address, nonce):
    return to_checksum_address(
        "0x" + keccak(encode([bytes.fromhex(address[2:]), nonce])).hex()[-40:]
    )


def get_create2_address(address, salt, init_code_hash):
    pre = "0xff"
    b_pre = bytes.fromhex(pre[2:])
    b_address = bytes.fromhex(address[2:])
    b_salt = bytes.fromhex(salt[2:])
    b_init_code = bytes.fromhex(init_code_hash[2:])

    b_result = keccak(b_pre + b_address + b_salt + b_init_code)

    result_address = to_checksum_address(b_result[12:].hex())

    return result_address
