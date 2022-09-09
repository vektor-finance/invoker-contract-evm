import binascii
import pickle
from contextlib import contextmanager
from enum import Enum
from functools import wraps

import brownie
from brownie import interface, web3
from brownie.exceptions import VirtualMachineError
from eth_abi import encode_single
from eth_utils import keccak

from data.chain import get_chain_id


@contextmanager
def isolate_fixture():
    brownie.chain.snapshot()
    try:
        yield
    finally:
        brownie.chain.revert()


class DisableTrace(object):
    def __init__(self, web3) -> None:
        self.web3 = web3
        self.initial_traces = web3._supports_traces

    def __enter__(self):
        self.web3._supports_traces = False

    def __exit__(self, type, value, traceback):
        self.web3._supports_traces = self.initial_traces


def cached(func):
    try:
        with open("data/balances_cache.pkl", "rb") as infile:
            func.cache = pickle.load(infile)
    except FileNotFoundError:
        func.cache = {}

    @wraps(func)
    def wrapper(*args):
        try:
            return func.cache[args]
        except KeyError:
            func.cache[args] = result = func(*args)
            with open("data/balances_cache.pkl", "wb") as outfile:
                pickle.dump(func.cache, outfile)
            return result

    return wrapper


def bytes32(i):
    return binascii.unhexlify("%064x" % i)


def get_storage_key(address, storage_slot):
    user = int(address, 16)
    key = bytes32(user) + bytes32(storage_slot)
    return "0x" + keccak(key).hex()


def get_balance_slot(token, network):
    user = "0x1234567890123456789012345678901234567890"
    token = interface.ERC20Detailed(token)

    tx = token.balanceOf.transact(user, {"from": user})
    trace = tx.trace
    sha_opcode = [t for t in trace if t["op"] == "SHA3"][-1]

    word_offset = int(sha_opcode["stack"][-1], 16) // 32
    assert (
        sha_opcode["stack"][-2]
        == "0000000000000000000000000000000000000000000000000000000000000040"
    )
    balances_slot = int("0x" + sha_opcode["memory"][word_offset + 1], 16)

    storage_address = sha_opcode["address"]

    for subcall in tx.subcalls[::-1]:
        if subcall["op"] == "DELEGATECALL":
            storage_address = subcall["from"]
        else:
            break

    return storage_address, balances_slot


class MintStrategy(Enum):
    NATIVE = 0
    BALANCES = 1
    BENEFACTOR = 2


BENEFACTORS = {
    "1": {
        "0x028171bca77440897b824ca71d1c56cac55b68a3": "0x0d33c811d0fcc711bcb388dfb3a152de445be66f",
        "0xbcca60bb61934080951369a648fb03df4f96263c": "0x87d48c565d0d85770406d248efd7dc3cbd41e729",
        "0x3ed3b47dd13ec9a98b44e6204a523e766b225811": "0x87d48c565d0d85770406d248efd7dc3cbd41e729",
        "0x6c5024cd4f8a59110119c56f8933403a539555eb": "0xa2a3cae63476891ab2d640d9a5a800755ee79d6e",
        "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
        "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490": "0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a",
        "0xd533a949740bb3306d119cc777fa900ba034cd52": "0x5f3b5dfeb7b28cdbd7faba78963ee202a494e2a2",
        "0xc4ad29ba4b3c580e6d59105fff484999997675ff": "0xdefd8fdd20e0f34115c7018ccfb655796f6b2168",
        "0x075b1bb99792c9e1041ba13afef80c91a1e70fb3": "0x13c1542a468319688b89e323fe9a3be3a90ebb27",
        "0x674c6ad92fd080e4004b2312b45f796a192d27a0": "0x868d94b174bed780717cf62e7ed31653638d5948",
        "0x9d409a0a012cfba9b15f6d4b36ac57a46966ab9a": "0x66ca70f1a348bdc66bb201e09eae4009d1d1e7e8",
        "0x8751d4196027d4e6da63716fa7786b5174f04c15": "0x042b32ac6b453485e357938bdc38e0340d4b9276",
        "0x683923db55fead99a79fa01a27eec3cb19679cc3": "0xafbd7bd91b4c1dd289ee47a4f030fbedfa7abc12",
        "0x65f7ba4ec257af7c55fd5854e5f6356bbd0fb8ec": "0xf977814e90da44bfa03b6295a0616a897441acec",
        "0x3472a5a71965499acd81997a54bba8d852c6e53d": "0xd0a7a8b98957b9cd3cfb9c0425abe44551158e9e",
        "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86": "0x87650d7bbfc3a9f10587d7778206671719d9910d",
        "0x9fcf418b971134625cdf38448b949c8640971671": "0x3fb78e61784c9c637d560ede23ad57ca1294c14a",
        "0xf0a93d4994b3d98fb5e3a2f90dbc2d69073cb86b": "0xbcb91e689114b9cc865ad7871845c95241df4105",
        "0xd01ef7c0a5d8c432fc2d1a85c66cf2327362e5c6": "0xc437df90b37c1db6657339e31bfe54627f0e7181",
        "0x3175df0976dfa876431c2e9ee6bc45b65d3473cc": "0xcfc25170633581bf896cb6cdee170e3e3aa59503",
        "0xd46ba6d942050d489dbd938a2c909a5d5039a161": "0xc3a947372191453dd9db02b0852d378dccbdf271",
        "0xdf7ff54aacacbff42dfe29dd6144a69b629f8c9e": "0x1a5023cc3067da8cc1f5e7846d3a3662c954416a",
        "0xd4937682df3c8aef4fe912a96a74121c0829e664": "0x02577b426f223a6b4f2351315a19ecd6f357d65c",
        "0x6f634c6135d2ebd550000ac92f494f9cb8183dae": "0x09c21f950ecb6b714e08d4411764c5036e53eba9",
        "0x5165d24277cd063f5ac44efd447b27025e888f37": "0x22925707d59f89c2edf103b79436fce932d559eb",
        "0xb9d7cb55f463405cdfbe4e90a6d2df01c2b92bf1": "0xf929122994e177079c924631ba13fb280f5cd1f9",
        "0x030ba81f1c18d280636f32af80b9aad02cf0854e": "0x4093fbe60ab50ab79a5bd32fa2adec255372f80e",
        "0x05ec93c0365baaeabf7aeffb0972ea7ecdd39cf1": "0xa2ebd97892502847061fe611efd5e289dbfa0703",
        "0xffc97d72e13e01096502cb8eb52dee56f74dad7b": "0x4a49985b14bd0ce42c25efde5d8c379a48ab02f3",
        "0x9ff58f4ffb29fa2266ab25e75e2a8b3503311656": "0xa976ea51b9ba3232706af125a92e32788dc08ddc",
        "0x272f97b7a56a387ae942350bbc7df5700f8a4576": "0x6724f3fbb16f542401bfc42c464ce91b6c31001e",
        "0xd37ee7e4f452c6638c96536e68090de8cbcdb583": "0x044b48e46b0b7b8b639364cc90875a0f7d4537ec",
        "0x8dae6cb04688c62d939ed9b68d32bc62e49970b1": "0x7a16ff8270133f063aab6c9977183d9e72835428",
        "0x101cc05f4a51c0319f570d5e146a8c625198e636": "0x611f97d450042418e7338cbdd19202711563df01",
        "0x35f6b052c598d933d69a4eec4d04c73a191fe6c2": "0xeedbe79de6cd498d051a632f22dd89d472876e8f",
        "0xcc12abe4ff81c9378d670de1b57f8e0dd228d77a": "0x13e1e72a57e58b710f60d801268c572e4283b551",
        "0xc713e5e149d5d0715dcd1c156a020976e7e56b88": "0x638e9ad05dbd35b1c19df3a4eaa0642a3b90a2ad",
        "0xa685a61171bb30d4072b338c80cb7b2c865c873e": "0x23b4f89e21c82aa54a7cfa263b36e724e70dd69a",
        "0xa06bc25b5805d5f8d82847d191cb4af5a3e873e0": "0x4a470942dd7a44c6574666f8bda47ce33c19a601",
        "0xac6df26a590f08dcc95d5a4705ae8abbc88509ef": "0xa937f63ba1d69fd7e022fd50628b6d8fcfbde52d",
        "0xa361718326c15715591c299427c62086f69923d9": "0x63dbd79851ec6793d70981d18809d49fd14eba19",
        "0x2e8f4bdbe3d47d7d7de490437aea9915d930f1a3": "0x9f2ca760aa9593d677e0753622e2adda8cc39f1c",
        "0x1e6bb68acec8fefbd87d192be09bb274170a0548": "0x755cf0c9cd59d6f83a7a0276f81dde9cccddbfeb",
        "0xc9bc48c72154ef3e5425641a3c747242112a46af": "0x02cbe7feaa8b969acc43ab368b6ed45cb63f3354",
        "0x514cd6756ccbe28772d4cb81bc3156ba9d1744aa": "0x87f91943345923039182ab2444b686dbc7c4a200",
        "0xf256cc7847e919fac9b808cc216cac87ccf2f47a": "0x6914fc70fac4cab20a8922e900c4ba57feecf8e1",
        "0x1982b2f5814301d4e9a8b0201555376e62f82428": "0x638e9ad05dbd35b1c19df3a4eaa0642a3b90a2ad",
        "0x9a14e23a58edf4efdcb360f68cd1b95ce2081a2f": "0x4e5cb586c2ee0d0f42891b705061d2ea42b236dc",
        "0x952749e07d7157bb9644a894dfaf3bad5ef6d918": "0x6db65261a4fc3f88e60b7470e9b38db0b22e785c",
        "0xb29130cbcc3f791f077eade0266168e808e5151e": "0x24c47db1cc0ba028836bf808175c044055d037ec",
    },
    "10": {
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0x061b87122ed14b9526a813209c8a59a633257bab"
    },
    "137": {
        "0x27f8d03b3a2196956ed754badc28d73be8830a6e": "0xe6c23289ba5a9f0ef31b8eb36241d5c800889b7b",
        "0x1a13f4ca1d028320a707d99520abfefca3998b7f": "0xd4f6d570133401079d213ecf4a14fa0b4bfb5b9c",
        "0x60d55f02a771d515e077c9c2403a1ef324885cec": "0xeab7831c96876433db9b8953b4e7e8f66c3125c3",
        "0x5c2ed810328349100a66b82b78a1791b101c9d61": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0xe7a24ef0c5e95ffb0f6684b813a78f2a3ad7d171": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0x28424507fefb6f7f8e9d3860f56504e4e5f5f390": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0x013f9c3fac3e2759d7e90aca4f9540f75194a0d7": "0xd30dcad4c32091d3b7c7582329787671abcc65fb",
        "0xad326c253a84e9805559b73a08724e11e49ca651": "0x1e1506b8cf84f8d1c2dbf474bcb6fec36467c478",
        "0x1ddcaa4ed761428ae348befc6718bcb12e63bfaa": "0xda43bfd7ecc6835aa6f1761ced30b986a574c0d2",
        "0xa8d394fe7380b8ce6145d5f85e6ac22d4e91acde": "0x7a602815908e1615393148a7880a7fc9e57949ae",
        "0xc4195d4060daeac44058ed668aa5efec50d77ff6": "0x8832924854e3cedb0a6abf372e6ccff9f7654332",
        "0x81fb82aacb4abe262fc57f06fd4c1d2de347d7b1": "0x070657fbd7111bb23ca7df96f795b75075a2a08e",
        "0x8df3aad3a84da6b69a4da8aec3ea40d9091b2ac4": "0x8832924854e3cedb0a6abf372e6ccff9f7654332",
        "0x1d2a0e5ec8e5bbdca5cb219e649b565d8e5c3360": "0xea4040b21cb68afb94889cb60834b13427cfc4eb",
        "0x080b5bf8f360f624628e0fb961f4e67c9e3c7cf1": "0x975779102b2a82384f872ee759801db5204ce331",
        "0x3df8f92b7e798820ddcca2ebea7babda2c90c4ad": "0xb0898b883de7f7f49ab8622f2185f5d0ca25b2ad",
        "0x21ec9431b5b55c5339eb1ae7582763087f98fac2": "0xa342b29ade6837b519bd9067047e85edbe86e2ad",
        "0x0ca2e42e8c21954af73bc9af1213e4e81d6a669a": "0xb0898b883de7f7f49ab8622f2185f5d0ca25b2ad",
        "0x82e64f49ed5ec1bc6e43dad4fc8af9bb3a2312ee": "0xfe4adb19631c2684d6fedc354e5bd1b76bf01cba",
        "0x191c10aa4af7c30e871e70c95db0e4eb77237530": "0xf3ad7d08240b09d0ee8ac0811fbee835ce2788e1",
        "0x625e7708f30ca75bfd92586e17077590c60eb4cd": "0x65a7b4ff684c2d08c115d55a4b089bf4e92f5003",
        "0x078f358208685046a11c85e8ad32895ded33a249": "0xe9177c5204f633a562747010788903747a858dcd",
        "0xe50fa9b3c56ffb159cb0fca61f5c9d750e8128c8": "0x4a16ac778f418b531d89a0f7bf6a4b2d12fd252a",
        "0x6ab707aca953edaefbc4fd23ba73294241490620": "0xac4b7ee2600f9bdc73f2bbe9b721a8a8b0a4d776",
        "0xf329e36c7bf6e5e86ce2150875a84ce77f477375": "0x9824697f7c12cabada9b57842060931c48dea969",
        "0x6d80113e533a2c0fe82eabd35f1875dcea89ea97": "0x5c5a4ae893c4232a050b01a84e193e107dd80ca2",
        "0x513c7e3a9c69ca3e22550ef58ac1c0088e918fff": "0x4ef7a7c9036e1f324f9cd83efa5b3ad94f27f4d1",
        "0xc45a479877e1e9dfe9fcd4056c699575a1045daa": "0x6cf9aa65ebad7028536e353393630e2340ca6049",
        "0x8eb270e296023e9d92081fdf967ddd7878724424": "0x73958d46b7aa2bc94926d8a215fa560a5cdca3ea",
        "0x8ffdf2de812095b1d19cb146e4c004587c0a0692": "0xe5facaef11b03766cf44a9bf629f551fa2355e54",
        "0x724dc807b04555b71ed48a6896b6f41593b8c637": "0x2562a449a01333cc661e7d6da287b49c3dc3f1a0",
        "0x38d693ce1df5aadf7bc62595a37d667ad57922e5": "0xebf6c10b74747f73abe5c22c6599b0e05fcd1c31",
        "0x6533afac2e7bccb20dca161449a13a32d391fb00": "0x2709fa6fa31bd336455d4f96ddfc505b3aca5a68",
        "0x8437d7c167dfb82ed4cb79cd44b7a32a1dd95c77": "0xda2d2f638d6fcbe306236583845e5822554c02ea",
    },
    "250": {
        "0x27e611fd27b276acbd5ffd632e5eaebec9761e40": "0x15bb164f9827de760174d3d3dad6816ef50de13c",
        "0x07e6332dd090d287d3489245038daf987955dcfb": "0x49c93a95dbcc9a6a4d8f77e59c038ce5020e82f8",
        "0xe578c856933d8e1082740bf7661e379aa2a30b26": "0xd1a992417a0abffa632cbde4da9f5dcf85caa858",
        "0x940f41f0ec9ba1a34cf001cc03347ac092f5f6b5": "0xec51fffe35f5b2b841103cfc5d4f5eb22c8fa33e",
        "0xd02a30d33153877bc20e5721ee53dedee0422b2f": "0xf7b9c402c4d6c2edba04a7a515b53d11b1e9b2cc",
        "0xb42bf10ab9df82f9a47b86dd76eee4ba848d0fa2": "0x9b9e258b3dace1d814f697a9d9816c5e4a8b6736",
        "0x25c130b2624cf12a4ea30143ef50c5d68cefa22f": "0x108383e62992b9a90ed3a43c2c9fa26ca052d99b",
        "0x39b3bd37208cbade74d0fcbdbb12d606295b430a": "0x212a9507ce6d0ac42990bf42db14d922a2a6beed",
        "0x38aca5484b8603373acc6961ecd57a6a594510a3": "0x9746447d8f9d1dedd70a470e419dfc472a7ebba5",
        "0x690754a168b022331caa2467207c61919b3f8a98": "0x64cf81f703981f22add30e0c9cecc766141a30c0",
        "0xc664fc7b8487a3e10824cda768c1d239f2403bbe": "0x2d960e1e1098681c124c111b206316772fe023d8",
        "0xbecf29265b0cc8d33fa24446599955c7bcf7f73b": "0xb851d31ff1c2dd4fa2f4b584e833202f500c90a7",
        "0x8e4bfb85962a63cacfa2c0fde5ead86d9b120b16": "0x2f07c8de8b633a7b4278b28c09a654295d8eeefb",
        "0x0638546741f12fa55f840a763a5aef9671c74fc1": "0x66bf43cc844a3c6b69d4c5aa39ba97f1e73f9bed",
        "0x6cbe07b362f2be4217a5ce247f07c422b0bd88f3": "0xb307d426a34a72a94b32bca5c5f0c8b36440fa80",
        "0xf3cb6762f5c159a1494b01c50a131d7f2b24fb14": "0x369606edde71fb6ec43353330796544852bad340",
        "0xa44e588ec78066d27f768f4901a2577f821938a1": "0x3452f7317404570b49de149923aad4e28cd715d7",
        "0x98d5105370191d641f32589b35cda9ecd367c74f": "0xdbf1d832d1e66ce1d8498d578364c0d7d0614c7b",
        "0x37d17a09f662d0145d1b4d6182d0cbeb8b90f9b7": "0x66bf43cc844a3c6b69d4c5aa39ba97f1e73f9bed",
        "0x072d8851075ca70f1112ae54fc508fe2fa62bb5a": "0x17451598bf282da2367e3fd1823f871f4b42b9f9",
        "0x4bef26fa85c3b5c620c760f8f5427a520d9a0565": "0x61fdd6e96581ceda2dd5ec6e4f61e2e89f97bd44",
    },
    "42161": {
        "0x7f90122bf0700f9e7e1f688fe926940e8839f353": "0xbf7e49483881c76487b0989cd7d9a8239b20ca41",
        "0xcab86f6fb6d1c2cbeeb97854a0c023446a075fe3": "0x0a824b5d4c96ea0ec46306efbd34bf88fe1277e0",
        "0x1ddcaa4ed761428ae348befc6718bcb12e63bfaa": "0x76b44e0cf9bd024dbed09e1785df295d59770138",
        "0x2d871631058827b703535228fb9ab5f35cf19e76": "0x5180db0237291a6449dda9ed33ad90a38787621c",
        "0x625e7708f30ca75bfd92586e17077590c60eb4cd": "0xc9032419aa502fafa107775dca8b7d07575d9db5",
        "0x6ab707aca953edaefbc4fd23ba73294241490620": "0x4fb361c9ce167d4049a50b42cf1db57161820cbd",
        "0x82e64f49ed5ec1bc6e43dad4fc8af9bb3a2312ee": "0x8cd67407f05526c57760d0e911d60c57b7e85c8e",
        "0x4cd44e6fcfa68bf797c65889c74b26b8c2e5d4d3": "0x4cc25e0366c564847546f2feda3d7f0d9155b9ac",
        "0xef47ccc71ec8941b67dc679d1a5f78facfd0ec3c": "0xc2054a8c33bfce28de8af4af548c48915c455c13",
        "0x805ba50001779ced4f59cff63aea527d12b94829": "0xc2054a8c33bfce28de8af4af548c48915c455c13",
        "0x5293c6ca56b8941040b8d18f557dfa82cf520216": "0xc2054a8c33bfce28de8af4af548c48915c455c13",
        "0x15b53d277af860f51c3e6843f8075007026bbb3a": "0xc2054a8c33bfce28de8af4af548c48915c455c13",
    },
    "43114": {
        "0x47afa96cdc9fab46904a55a6ad4bf6660b53c38a": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x46a51127c3ce23fb7ab1de06226147f446e4a857": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x532e6537fea298397212f09a61e03311686f548e": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x686bef2417b6dc32c50a3cbfbcc3bb60e1e9a15d": "0x16a7da911a4dd1d83f3ff066fe28f3c792c50d90",
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0x4620d46b4db7fb04a01a75ffed228bc027c9a899",
        "0x53f7c5869a859f0aec3d334ee8b4cf01e3492f21": "0xb755b949c126c04e0348dd881a5cf55d424742b2",
        "0x6807ed4369d9399847f306d7d835538915fa749d": "0xa867c1aca4b5f1e0a66cf7b1fe33525d57608854",
        "0xc25ff1af397b76252d6975b4d7649b35c0e60f69": "0x06960627461629409a087af6da50fe4d38d74f7e",
        "0x18cb11c9f2b6f45a7ac0a95efd322ed4cf9eeebf": "0xa5ad811c4b2bd8161090e97c946e1a2003989599",
        "0x28690ec942671ac8d9bc442b667ec338ede6dfd3": "0xd39016475200ab8957e9c772c949ef54bda69111",
    },
    "100": {
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0xb721cc32160ab0da2614cc6ab16ed822aeebc101",
        "0x6ac78efae880282396a335ca2f79863a1e6831d4": "0x53811010085382d49ef12bcc55902bbfceb57790",
    },
    "56": {},
    "1284": {},
    "1285": {},
}

NATIVES = [
    "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
]

OVERRIDES = {
    "1": {
        "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0": (
            MintStrategy.BENEFACTOR,
            "0xc8418af6358ffdda74e09ca9cc3fe03ca6adc5b0",
        )
    },
    "10": {},
    "137": {},
    "250": {
        "0x841FAD6EAe12c286d1Fd18d1d525DFfA75C7EFFE": (
            MintStrategy.BENEFACTOR,
            "0xa48d959ae2e88f1daa7d5f611e01908106de7598",
        )
    },
    "42161": {},
    "43114": {},
    "100": {},
    "56": {},
    "1284": {},
    "1285": {},
    "5": {},
}


class BenefactorError(Exception):
    pass


@cached
def get_mint_strategy(token, network):

    if token in OVERRIDES[network]:
        return OVERRIDES[network][token]

    user = "0x1234567890123456789012345678901234567890"

    if token.lower() in NATIVES:
        return (MintStrategy.NATIVE, None)

    try:
        balance_contract, balance_slot = get_balance_slot(token, network)
        user_slot = get_storage_key(user, balance_slot)
        encoded_value = "0x" + encode_single("uint256", 123456789).hex()
        web3.provider.make_request(
            "hardhat_setStorageAt", [balance_contract, user_slot, encoded_value]
        )
        assert interface.ERC20Detailed(token).balanceOf(user) == 123456789
        return (MintStrategy.BALANCES, (balance_contract, balance_slot))
    except (AssertionError):
        if token.lower() in BENEFACTORS[network]:
            return (MintStrategy.BENEFACTOR, BENEFACTORS[network][token.lower()])
        else:
            raise BenefactorError(f"{interface.ERC20Detailed(token).name()} - {token} - {network}")


def strip_zeros(val):
    # If the storage slot has a leading 0, hardhat gives us an error
    # this removes any leading zeroes
    return hex(int(val, 16))


def mint_tokens_for(token, user, amount=0):
    if hasattr(user, "address"):
        user = user.address
    if hasattr(token, "address"):
        token = token.address

    active_network = str(get_chain_id())
    strategy, params = get_mint_strategy(token, active_network)

    if strategy == MintStrategy.NATIVE:
        if amount == 0:
            amount = 1e18
        web3.provider.make_request("hardhat_setBalance", [user, hex(int(amount))])
        return amount

    elif strategy == MintStrategy.BALANCES:
        token = interface.ERC20Detailed(token)
        if amount == 0:
            amount = 10 ** token.decimals()

        user_slot = strip_zeros(get_storage_key(user, params[1]))
        encoded_value = "0x" + encode_single("uint256", int(amount)).hex()
        web3.provider.make_request("hardhat_setStorageAt", [params[0], user_slot, encoded_value])

    elif strategy == MintStrategy.BENEFACTOR:
        token = interface.ERC20Detailed(token)
        if amount == 0:
            amount = 10 ** token.decimals()

        try:
            token.transfer(user, amount, {"from": params})
        except VirtualMachineError:
            raise BenefactorError(f"{token.name()} - {token.address} - {active_network}")

    return amount
