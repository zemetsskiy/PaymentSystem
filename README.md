# PaymentSystem

## Getting Started

### Installing

A step by step series of examples that tell you how to get a development environment running:

1. Install the required dependencies:
   
   ```
   pip install -r requirements.txt
   ```

## Configuration

Before running the project, you need to configure it. The configuration settings are located in the `config.py` file. This includes the following key components:

- **Redis Setup**: Configure `REDIS_HOST`, `REDIS_PASSWD`, `REDIS_PORT` according to your Redis server settings in `config.py`.

- **Blockchain Nodes**: Set `POLYGON_NODE_URL`, `ARBITRUM_NODE_URL`, and `SEPOLIA_NODE_URL` in `config.py` to interact with the respective blockchain networks.

- **Email Notifications**: Configure `GMAIL_USER` and `GMAIL_PASSWORD` in `config.py` for sending email notifications.

- **Discord Integration**: Set the  and `GUILD_ID`, `TOKEN `, `ROLE_NAME `  as per your Discord application settings in `config.py`.

- **Discord OAuth2**: `DISCORD_OAUTH2_URL`, `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, `SCOPE` is set up in `config.py` for Discord OAuth2 functionality.

### Environment Variables

Ensure these environment variables are set in `config.py`:


## Running the Project

To run the project, use the following command:

```
python3 index.py
```
