CLIENT_ID = '1170419838716498081'
CLIENT_SECRET = 'HP5rk0hGTXAlejOWCLl8dGpO3WLO3CqW'
REDIRECT_URI = 'http://localhost:5000/oauth2/callback'
SCOPE = 'identify%20guilds%20guilds.join'
REDIS_HOST = "redis-14206.c8.us-east-1-4.ec2.cloud.redislabs.com"
REDIS_PASSWD = 'bex3QY76ZJoJsh4jwg8LCh3cqLQg0zSb'
REDIS_PORT = 14206

POLYGON_NODE_URL = "https://polygon-mainnet.infura.io/v3/7eec932e2c324e20ac051e0aa3741d9f"
ARBITRUM_NODE_URL = "https://arbitrum-mainnet.infura.io/v3/7eec932e2c324e20ac051e0aa3741d9f"
SEPOLIA_NODE_URL = "https://sepolia.infura.io/v3/7eec932e2c324e20ac051e0aa3741d9f"


# ==== GMAIL =====
GMAIL_USER = 'artem.tretykov74@gmail.com'
GMAIL_PASSWORD = 'gkmu wlsh sqmd epdk'

# ==== DISCORD =====
TOKEN = "MTE3MjI0MTAxMTg5MjgxNzk5Mg.GIdR16.jN3-lpArk4-ZRPD4-FuSIHJ6QKBNHsBorhfhbQ"
GUILD_ID = "1172234446456508476"
ROLE_NAME = "lame"


DISCORD_OAUTH2_URL = (
    f'https://discord.com/api/oauth2/authorize'
    f'?client_id={CLIENT_ID}'
    f'&redirect_uri={REDIRECT_URI}'
    f'&response_type=code'
    f'&scope={SCOPE}'
)
