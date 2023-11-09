from dataclasses import dataclass
from web3 import Web3
from web3.auto import w3
from config import POLYGON_NODE_URL, SEPOLIA_NODE_URL, ARBITRUM_NODE_URL


@dataclass
class Data:

    # TODO MORE NETWORKS AND TOKENS

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
    """
    A class to handle wallet generation and token balance checks for different networks.

    Attributes:
        polygon_w3 (Web3): An instance of Web3 connected to the Polygon network.
        arbitrum_w3 (Web3): An instance of Web3 connected to the Arbitrum network.
        sepolia_w3 (Web3): An instance of Web3 connected to the Sepolia testnet.
    """

    def __init__(self):
        """
        Initializes the Payments class by setting up connections to the various Ethereum-based networks.
        """
        self.polygon_w3 = Web3(Web3.HTTPProvider(POLYGON_NODE_URL))
        self.arbitrum_w3 = Web3(Web3.HTTPProvider(ARBITRUM_NODE_URL))
        self.sepolia_w3 = Web3(Web3.HTTPProvider(SEPOLIA_NODE_URL))

    @staticmethod
    async def generate_wallet():
        """
        Generates a new Ethereum wallet with a mnemonic phrase.

        Returns:
            tuple: A tuple containing the address, private key, and mnemonic phrase for the new wallet.
        """
        w3.eth.account.enable_unaudited_hdwallet_features()
        new_account = w3.eth.account.create_with_mnemonic()
        address = new_account[0].address
        private_key = new_account[0]._private_key.hex()
        mnemonic = new_account[1]
        return address, private_key, mnemonic

    async def get_token_balance(self, w3, address, token, network):
        """
        Fetches the token balance for a given address on a specified network.

        Args:
            w3 (Web3): The Web3 instance connected to the desired network.
            address (str): The address to query the balance for.
            token (str): The token symbol to query the balance of.
            network (str): The network to query the balance on.

        Returns:
            float: The balance of the token for the given address.
        """
        contract_address = Data.CONTRACT_ADDRESSES[network][token]
        token_contract = w3.eth.contract(address=contract_address, abi=Data.ERC20_ABI)
        balance = token_contract.functions.balanceOf(Web3.to_checksum_address(address)).call()

        decimals = token_contract.functions.decimals().call()
        readable_balance = balance / (10 ** decimals)

        return readable_balance

    async def check_token_transaction(self, w3, address, expected_amount, token, network):
        """
        Checks if a token transaction meets or exceeds an expected amount.

        Args:
            w3 (Web3): The Web3 instance connected to the desired network.
            address (str): The address to check the transaction for.
            expected_amount (str): The expected amount of tokens.
            token (str): The token symbol to check the transaction of.
            network (str): The network to check the transaction on.

        Returns:
            bool: True if the balance meets or exceeds the expected amount, False otherwise.
        """
        if token.lower() == 'eth':
            balance = w3.eth.get_balance(w3.to_checksum_address(address))
            balance_in_eth = w3.from_wei(balance, 'ether')
            return balance_in_eth >= 0.97 * float(expected_amount)
        else:
            balance = await self.get_token_balance(w3, w3.to_checksum_address(address), token, network)
            return balance >= 0.97 * float(expected_amount)

    async def start_payment_session(self, expected_amount, address, token, network):
        """
        Starts a payment session by checking if the received amount of tokens at an address is as expected.

        Args:
            expected_amount (float): The amount of tokens expected to receive.
            address (str): The wallet address to monitor for incoming tokens.
            token (str): The token symbol to monitor.
            network (str): The network where the address is to be monitored.

        Returns:
            tuple: A tuple containing a boolean indicating success, and a string indicating the network, if successful.
        """

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