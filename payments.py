from dataclasses import dataclass
from web3 import Web3
from web3.auto import w3


@dataclass
class Data:
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        }
    ]

    CONTRACT_ADDRESSES = {
        'polygon': {
            'USDT': Web3.to_checksum_address('0xc2132D05D31c914a87C6611C10748AEb04B58e8F'),
            'USDC': Web3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
        },
        'arbitrum': {
            'USDT': Web3.to_checksum_address('0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9'),
            'USDC': Web3.to_checksum_address('0xaf88d065e77c8cc2239327c5edb3a432268e5831')
        }
    }


class Payments:
    POLYGON_NODE_URL = "https://polygon-mainnet.infura.io/v3/7eec932e2c324e20ac051e0aa3741d9f"
    ARBITRUM_NODE_URL = "https://arbitrum-mainnet.infura.io/v3/7eec932e2c324e20ac051e0aa3741d9f"
    SEPOLIA_NODE_URL = "https://sepolia.infura.io/v3/7eec932e2c324e20ac051e0aa3741d9f"

    def __init__(self):
        self.polygon_w3 = Web3(Web3.HTTPProvider(Payments.POLYGON_NODE_URL))
        self.arbitrum_w3 = Web3(Web3.HTTPProvider(Payments.ARBITRUM_NODE_URL))
        self.sepolia_w3 = Web3(Web3.HTTPProvider(Payments.SEPOLIA_NODE_URL))

    @staticmethod
    async def generate_wallet():
        w3.eth.account.enable_unaudited_hdwallet_features()
        new_account = w3.eth.account.create_with_mnemonic()
        address = new_account[0].address
        private_key = new_account[0]._private_key.hex()
        mnemonic = new_account[1]
        return address, private_key, mnemonic

    async def get_token_balance(self, w3, address, token, network):
        contract_address = Data.CONTRACT_ADDRESSES[network][token]
        token_contract = w3.eth.contract(address=contract_address, abi=Data.ERC20_ABI)
        balance = token_contract.functions.balanceOf(Web3.to_checksum_address(address)).call()

        decimals = token_contract.functions.decimals().call()
        readable_balance = balance / (10 ** decimals)

        return readable_balance

    async def check_token_transaction(self, w3, address, expected_amount, token, network):
        if token.lower() == 'eth':
            balance = w3.eth.get_balance(w3.to_checksum_address(address))
            balance_in_eth = w3.from_wei(balance, 'ether')
            return balance_in_eth >= 0.97 * float(expected_amount)
        else:
            balance = await self.get_token_balance(w3, w3.to_checksum_address(address), token, network)
            return balance >= 0.97 * float(expected_amount)

    async def start_payment_session(self, expected_amount, address, token, network):

        if network == "ethereum":
            if token == "ETH":
                pass
            elif token == "USDT":
                pass
            elif token == "USDC":
                pass

        elif network.lower() == "sepolia":
            if token == "eth":
                res = await self.check_token_transaction(self.sepolia_w3, address, expected_amount, 'ETH', 'sepolia')
                if res:
                    return True, "sepolia"

        elif network == "polygon":
            if token == "ETH":
                pass
            elif token == "USDT":
                if await self.check_token_transaction(self.polygon_w3, address, expected_amount, 'USDT', 'polygon'):
                    return True, "polygon"

            elif token == "USDC":
                if await self.check_token_transaction(self.polygon_w3, address, expected_amount, 'USDC', 'polygon'):
                    return True, "polygon"

        elif network == "arbitrum":
            if token == "ETH":
                pass
            elif token == "USDT":
                if await self.check_token_transaction(self.arbitrum_w3, address, expected_amount, 'USDT', 'arbitrum'):
                    return True, "arbitrum"

            elif token == "USDC":
                if await self.check_token_transaction(self.arbitrum_w3, address, expected_amount, 'USDC', 'arbitrum'):
                    return True, "arbitrum"

        return False, "-"