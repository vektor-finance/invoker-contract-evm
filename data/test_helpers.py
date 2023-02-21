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
        "0x3ed3b47dd13ec9a98b44e6204a523e766b225811": "0x05bc11f64c6515bb384b05bfd3e0d0424fa65aa4",
        "0x6c5024cd4f8a59110119c56f8933403a539555eb": "0xa2a3cae63476891ab2d640d9a5a800755ee79d6e",
        "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
        "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490": "0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a",
        "0xd533a949740bb3306d119cc777fa900ba034cd52": "0x5f3b5dfeb7b28cdbd7faba78963ee202a494e2a2",
        "0xc4ad29ba4b3c580e6d59105fff484999997675ff": "0xdefd8fdd20e0f34115c7018ccfb655796f6b2168",
        "0x075b1bb99792c9e1041ba13afef80c91a1e70fb3": "0x13c1542a468319688b89e323fe9a3be3a90ebb27",
        "0x674c6ad92fd080e4004b2312b45f796a192d27a0": "0x868d94b174bed780717cf62e7ed31653638d5948",
        "0x9d409a0a012cfba9b15f6d4b36ac57a46966ab9a": "0x9461173740d27311b176476fa27e94c681b1ea6b",
        "0x8751d4196027d4e6da63716fa7786b5174f04c15": "0xfbdca68601f835b27790d98bbb8ec7f05fdeaa9b",
        "0x683923db55fead99a79fa01a27eec3cb19679cc3": "0x4094aec22f40f11c29941d144c3dc887b33f5504",
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
        "0x6f634c6135d2ebd550000ac92f494f9cb8183dae": "0x1c631824b0551FD0540A1f198c893B379D5Cf3c3",
        "0x5165d24277cd063f5ac44efd447b27025e888f37": "0x5bA6624Ed97EAdDC2a2b5778A2771716Eb4Ca96A",
        "0xb9d7cb55f463405cdfbe4e90a6d2df01c2b92bf1": "0x3e0182ccc2db35146e0529de779fb1025e8b0178",
        "0x030ba81f1c18d280636f32af80b9aad02cf0854e": "0x0cd420966fce68bad79cd82c9a360636cf898c1e",
        "0x05ec93c0365baaeabf7aeffb0972ea7ecdd39cf1": "0xa2ebd97892502847061fe611efd5e289dbfa0703",
        "0xffc97d72e13e01096502cb8eb52dee56f74dad7b": "0x4a49985b14bd0ce42c25efde5d8c379a48ab02f3",
        "0x9ff58f4ffb29fa2266ab25e75e2a8b3503311656": "0xa976ea51b9ba3232706af125a92e32788dc08ddc",
        "0x272f97b7a56a387ae942350bbc7df5700f8a4576": "0x10a19e7ee7d7f8a52822f6817de8ea18204f2e4f",
        "0xd37ee7e4f452c6638c96536e68090de8cbcdb583": "0xd5AC0D30b6059640ca089C608663562601d81B42",
        "0x8dae6cb04688c62d939ed9b68d32bc62e49970b1": "0x7a16ff8270133f063aab6c9977183d9e72835428",
        "0x101cc05f4a51c0319f570d5e146a8c625198e636": "0x3DdfA8eC3052539b6C9549F12cEA2C295cfF5296",
        "0x35f6b052c598d933d69a4eec4d04c73a191fe6c2": "0xeedbe79de6cd498d051a632f22dd89d472876e8f",
        "0xcc12abe4ff81c9378d670de1b57f8e0dd228d77a": "0xa58e7dab7b11de041353d6d3426b5a520bddb580",
        "0xc713e5e149d5d0715dcd1c156a020976e7e56b88": "0xa9DEE54892713F43c221509cfEdBd717D16791a0",
        "0xa685a61171bb30d4072b338c80cb7b2c865c873e": "0x23b4f89e21c82aa54a7cfa263b36e724e70dd69a",
        "0xa06bc25b5805d5f8d82847d191cb4af5a3e873e0": "0x4a470942dd7a44c6574666f8bda47ce33c19a601",
        "0xac6df26a590f08dcc95d5a4705ae8abbc88509ef": "0xa937f63ba1d69fd7e022fd50628b6d8fcfbde52d",
        "0xa361718326c15715591c299427c62086f69923d9": "0x63dbd79851ec6793d70981d18809d49fd14eba19",
        "0x2e8f4bdbe3d47d7d7de490437aea9915d930f1a3": "0x9f2ca760aa9593d677e0753622e2adda8cc39f1c",
        "0x1e6bb68acec8fefbd87d192be09bb274170a0548": "0x755cf0c9cd59d6f83a7a0276f81dde9cccddbfeb",
        "0xc9bc48c72154ef3e5425641a3c747242112a46af": "0x02cbe7feaa8b969acc43ab368b6ed45cb63f3354",
        "0x514cd6756ccbe28772d4cb81bc3156ba9d1744aa": "0x87f91943345923039182ab2444b686dbc7c4a200",
        "0xf256cc7847e919fac9b808cc216cac87ccf2f47a": "0x6914fc70fac4cab20a8922e900c4ba57feecf8e1",
        "0x1982b2f5814301d4e9a8b0201555376e62f82428": "0x94269a09c5fcbd5e88f9df13741997bc11735a9c",
        "0x9a14e23a58edf4efdcb360f68cd1b95ce2081a2f": "0x4e5cb586c2ee0d0f42891b705061d2ea42b236dc",
        "0x952749e07d7157bb9644a894dfaf3bad5ef6d918": "0x30dd12344ce6bb4596c37f68b507028fabfe2e0f",
        "0xb29130cbcc3f791f077eade0266168e808e5151e": "0x5e89f8d81c74e311458277ea1be3d3247c7cd7d1",
        "0x71df9dd3e658f0136c40e2e8ec3988a5226e9a67": "0xdd167502a53030f13fd362494e9ed3e0a189431b",
        "0xa693b19d2931d498c5b318df961919bb4aee87a5": "0x9a0cc6791a5409ce3547f1f1d00e058c79d0a72c",
        "0x99534ef705df1fff4e4bd7bbaaf9b0dff038ebfe": "0x99534ef705df1fff4e4bd7bbaaf9b0dff038ebfe",
        "0x973f054edbecd287209c36a2651094fa52f99a71": "0x5a59fd6018186471727faaeae4e57890abc49b08",
        "0x2a54ba2964c8cd459dc568853f79813a60761b58": "0x63aac74200ba1737f81beeaeda64a539d9883922",
        "0xee586e7eaad39207f0549bc65f19e336942c992f": "0xe7a3b38c39f97e977723bd1239c3470702568e7b",
        "0xfcc5c47be19d06bf83eb04298b026f81069ff65b": "0x27b5739e22ad9033bcbf192059122d163b60349d",
        "0x015b94ab2b0a14a96030573fbcd0f3d3d763541f": "0xf476d99f892c23b3ec828762eba2b46c3fda949f",
        "0xc22956c3cfec3ee9a9925abee044f05bc47f6632": "0x569c1f1fcced968120e631466a55fa7acfec5b79",
        "0x6b8734ad31d42f5c05a86594314837c416ada984": "0x066b6e1e93fa7dcd3f0eb7f8bac7d5a747ce0bf9",
        "0x92e187a03b6cd19cb6af293ba17f2745fd2357d5": "0x000000000000000000000000000000000000dead",
        "0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca": "0xeb31da939878d1d780fdbcc244531c0fb80a2cf3",
        "0x72953a5c32413614d24c29c84a66ae4b59581bbf": "0x84c82d43f1cc64730849f3e389fe3f6d776f7a4e",
        "0xb3ad645db386d7f6d753b2b9c3f4b853da6890b8": "0xe4c09928d834cd58d233cd77b5af3545484b4968",
    },
    "10": {
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0x061b87122ed14b9526a813209c8a59a633257bab",
        "0x82e64f49ed5ec1bc6e43dad4fc8af9bb3a2312ee": "0x36395bf7d30de794bc94f9e581cefc2d0257136c",
        "0x29a3d66b30bc4ad674a4fdaf27578b64f6afbfe7": "0x0df840dcbf1229262a4125c1fc559bd338ec9491",
        "0x625e7708f30ca75bfd92586e17077590c60eb4cd": "0x4ecb5300d9ec6bca09d66bfd8dcb532e3192dda1",
        "0x6ab707aca953edaefbc4fd23ba73294241490620": "0x8702c9a26d400ae1f996569fa508063fb26db0c0",
    },
    "137": {
        "0x27f8d03b3a2196956ed754badc28d73be8830a6e": "0xe6c23289ba5a9f0ef31b8eb36241d5c800889b7b",
        "0x1a13f4ca1d028320a707d99520abfefca3998b7f": "0xd4f6d570133401079d213ecf4a14fa0b4bfb5b9c",
        "0x60d55f02a771d515e077c9c2403a1ef324885cec": "0xeab7831c96876433db9b8953b4e7e8f66c3125c3",
        "0x5c2ed810328349100a66b82b78a1791b101c9d61": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0xe7a24ef0c5e95ffb0f6684b813a78f2a3ad7d171": "0x774d1dba98cfbd1f2bc3a1f59c494125e07c48f9",
        "0x28424507fefb6f7f8e9d3860f56504e4e5f5f390": "0x92215849c439e1f8612b6646060b4e3e5ef822cc",
        "0x013f9c3fac3e2759d7e90aca4f9540f75194a0d7": "0x0f4be7f70c820ed07926aaaa1216b7d7345bc923",
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
        "0xdad97f7713ae9437fa9249920ec8507e5fbb23d3": "0xbb1b19495b8fe7c402427479b9ac14886cbbaaee",
        "0x4318cb63a2b8edf2de971e2f17f77097e499459d": "0x7dab6054518f67ac69b0afa4c46ff16dd2bf560e",
        "0x576cf361711cd940cd9c397bb98c4c896cbd38de": "0x0213695eb4cf4f795397fcc6d3cd370143838e36",
        "0x40cab7c05fc1686e198c8d6d6aa4aacf77be8590": "0x3bfb65904cb66408bca4c73ebb548126dd77f3db",
        "0x3bfb65904cb66408bca4c73ebb548126dd77f3db": "0x622703d6517bdedf1fa5d076d30dcbb00ee18d5c",
        "0x622703d6517bdedf1fa5d076d30dcbb00ee18d5c": "0xcecf60b95109cb4c897b22877612228f0c76e52c",
        "0xe6469ba6d2fd6130788e0ea9c0a0515900563b59": "0x5180db0237291a6449dda9ed33ad90a38787621c",
        "0x038ff5771ed27e6f14409672285359b79107ead2": "0x3bfb65904cb66408bca4c73ebb548126dd77f3db",
        "0xcecf60b95109cb4c897b22877612228f0c76e52c": "0x1197ae7f43695be80127365b494e8bf850f4752a",
        "0x1197ae7f43695be80127365b494e8bf850f4752a": "0xd106fb0cfb6a3b6a8e9b08c19f8f4d39e4b4cda1",
        "0x84f168e646d31f6c33fdbf284d9037f59603aa28": "0xdde5fdb48b2ec6bc26bb4487f8e3a4eb99b3d633",
        "0xb52cfbca305e13c4c6774846f8d42bb1f0ec51d0": "0x54079d6b56dd329f4faab976985559924301e6a0",
        "0xc125d5429a1e1fc1946f40feffca1c7859bf1d80": "0x1215a6dec3c6b5e917813b64dd11ead2ba9e45f2",
        "0x8a95282517721cb7bbc539b8834073198e35ad07": "0xa0e8a70f28c5342e3e01b14ff899d7c5d2ce0ec0",
        "0x03a97594aa5ece130e2e956fc0ced2fea8ed8989": "0x72d13f3c78976df0028addca8b8e9a69256d9b0f",
        "0xecdcb5b88f8e3c15f95c720c51c71c9e2080525d": "0xf8aae8d5dd1d7697a4ec6f561737e68a2ab8539e",
        "0xd106fb0cfb6a3b6a8e9b08c19f8f4d39e4b4cda1": "0x1ed0855c93bb3eb531232d4350f49861b026d087",
        "0x8660108c91098f400c412529cf5be3e0a9eeac9d": "0x018e7a8a99a71ebf7694c8a01b255d6d981b3c20",
        "0x2d871631058827b703535228fb9ab5f35cf19e76": "0x5180db0237291a6449dda9ed33ad90a38787621c",
        "0x1b12bdef2d562e19dd3b8cb66f61f1e1b714d491": "0xb2a7146f28779f638c88b8b0f7dfc5ad9f8ea886",
        "0xa1ee546e2a53e86ea7e1c5d017af3fea1d1a9620": "0xd07e44fe7c8f1fadc4a17956a108f26aa879ed06",
        "0xb78f2fe5fde99727cd2388f8c4f682395f894c16": "0x000e9001dbe7fb0cb7a911626c5864da70a0ed30",
        "0x4d9e99efbd2ed279b2668289005d0071a79fd62b": "0xef978c32151f3fbdbca825a5de8011d29a84b7d9",
        "0x6c060ce95131427550201cb296fb09f3a52150d0": "0x2c04a1638643ed586268542bd05af7bae7096057",
        "0xb5dfabd7ff7f83bab83995e72a52b97abb7bcf63": "0xa138341185a9d0429b0021a11fb717b225e13e1f",
    },
    "250": {
        "0x27e611fd27b276acbd5ffd632e5eaebec9761e40": "0x15bb164f9827de760174d3d3dad6816ef50de13c",
        "0x07e6332dd090d287d3489245038daf987955dcfb": "0x49c93a95dbcc9a6a4d8f77e59c038ce5020e82f8",
        "0xe578c856933d8e1082740bf7661e379aa2a30b26": "0xd1a992417a0abffa632cbde4da9f5dcf85caa858",
        "0x940f41f0ec9ba1a34cf001cc03347ac092f5f6b5": "0x489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec",
        "0xd02a30d33153877bc20e5721ee53dedee0422b2f": "0xf7b9c402c4d6c2edba04a7a515b53d11b1e9b2cc",
        "0xb42bf10ab9df82f9a47b86dd76eee4ba848d0fa2": "0x69a9d376e7aad5ea7666acebeda97134e2b1d108",
        "0x846e4d51d7e2043c1a87e0ab7490b93fb940357b": "0x20dd72ed959b6147912c2e529f0a0c651c33c9ce",
    },
    "42161": {
        "0x7f90122bf0700f9e7e1f688fe926940e8839f353": "0xbf7e49483881c76487b0989cd7d9a8239b20ca41",
        "0xcab86f6fb6d1c2cbeeb97854a0c023446a075fe3": "0x0a824b5d4c96ea0ec46306efbd34bf88fe1277e0",
        "0x1ddcaa4ed761428ae348befc6718bcb12e63bfaa": "0x76b44e0cf9bd024dbed09e1785df295d59770138",
        "0x2d871631058827b703535228fb9ab5f35cf19e76": "0x5180db0237291a6449dda9ed33ad90a38787621c",
        "0x625e7708f30ca75bfd92586e17077590c60eb4cd": "0xc9032419aa502fafa107775dca8b7d07575d9db5",
        "0x6ab707aca953edaefbc4fd23ba73294241490620": "0x202e219f81d27f61fa2bbed1c8b1a6851a520015",
        "0x82e64f49ed5ec1bc6e43dad4fc8af9bb3a2312ee": "0xbb9e12627e086e886c61596e04edfd78481e5412",
    },
    "43114": {
        "0x47afa96cdc9fab46904a55a6ad4bf6660b53c38a": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x46a51127c3ce23fb7ab1de06226147f446e4a857": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x532e6537fea298397212f09a61e03311686f548e": "0x467b92af281d14cb6809913ad016a607b5ba8a36",
        "0x686bef2417b6dc32c50a3cbfbcc3bb60e1e9a15d": "0x16a7da911a4dd1d83f3ff066fe28f3c792c50d90",
        "0x1337bedc9d22ecbe766df105c9623922a27963ec": "0x4620d46b4db7fb04a01a75ffed228bc027c9a899",
        "0x53f7c5869a859f0aec3d334ee8b4cf01e3492f21": "0xb755b949c126c04e0348dd881a5cf55d424742b2",
        "0xc25ff1af397b76252d6975b4d7649b35c0e60f69": "0x06960627461629409a087af6da50fe4d38d74f7e",
        "0x28690ec942671ac8d9bc442b667ec338ede6dfd3": "0xd39016475200ab8957e9c772c949ef54bda69111",
        "0x82e64f49ed5ec1bc6e43dad4fc8af9bb3a2312ee": "0x5ba7fd868c40c16f7adfae6cf87121e13fc2f7a0",
        "0xb599c3590f42f8f995ecfa0f85d2980b76862fc1": "0xd79138c49c49200a1afc935171d1bdad084fdc95",
        "0x625e7708f30ca75bfd92586e17077590c60eb4cd": "0x733ee5446711e06612b66d5bfc292533bf620f24",
        "0x6c6f910a79639dcc94b4feef59ff507c2e843929": "0x6c6f910a79639dcc94b4feef59ff507c2e843929",
        "0xbdf3c7412eb426197da14ad084567c006f365d76": "0x7497bcb8e497c1aa7d2299f1ac0e47ff0a6a07c6",
        "0x6ab707aca953edaefbc4fd23ba73294241490620": "0x6946b0527421b72df7a5f0c0c7a1474219684e8f",
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
    "250": {},
    "42161": {},
    "43114": {},
    "100": {},
    "56": {},
    "1284": {
        "0xffffffff1fcacbd218edc0eba20fc2308c778080": (
            MintStrategy.BENEFACTOR,
            "0xc6e37086d09ec2048f151d11cdb9f9bbbdb7d685",
        )
    },
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
