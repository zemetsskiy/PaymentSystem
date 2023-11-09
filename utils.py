import aiohttp


class Helper:
    @staticmethod
    async def getEthPrice():
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ethereum' in data and 'usd' in data['ethereum']:
                        eth_to_usd = data['ethereum']['usd']
                        return float(eth_to_usd)
                return None

    @staticmethod
    async def convertUsdToEth(amount_in_usd):
        eth_price = await Helper.getEthPrice()
        if eth_price is not None:
            eth_amount = amount_in_usd / eth_price
            return eth_amount
        else:
            return None

    @staticmethod
    async def getPlanPrice(plan_name, token):
        if plan_name == "basic_1_month":
            if token == "eth":
                price = await Helper.convertUsdToEth(9)
                return price
            else:
                return 9
        elif plan_name == "basic_6_months":
            if token == "eth":
                price = await Helper.convertUsdToEth(18)
                return price
            else:
                return 18
        elif plan_name == "basic_lifetime":
            if token == "eth":
                price = await Helper.convertUsdToEth(49)
                return price
            else:
                return 49
        elif plan_name == "vip_1_month":
            if token == "eth":
                price = await Helper.convertUsdToEth(14)
                return price
            else:
                return 14
        elif plan_name == "vip_6_months":
            if token == "eth":
                price = await Helper.convertUsdToEth(36)
                return price
            else:
                return 36
        elif plan_name == "vip_lifetime":
            if token == "eth":
                price = await Helper.convertUsdToEth(79)
                return price
            else:
                return 79