import asyncio
import os
import httpx
import aioredis

from datetime import datetime
from quart import Quart, render_template, request, redirect, url_for, session, jsonify
from payments import Payments
from utils import Helper
from logger import logging as logger
from config import DISCORD_OAUTH2_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, REDIS_HOST, REDIS_PORT, REDIS_PASSWD, TOKEN as ds_token, GUILD_ID as guild_id, ROLE_NAME as role_name
from send_message import send_message
from add_role import assign_role_to_user

app = Quart(__name__)

app.secret_key = os.urandom(16)


@app.before_serving
async def startup():
    """
    Initializes the application by setting up a connection to the Redis server before the server starts serving requests.
    """
    app.redis = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        password=REDIS_PASSWD,
        encoding='utf-8'
    )


@app.after_serving
async def cleanup():
    """
    Closes the Redis connection after the app has finished serving.
    """
    await app.redis.close()


async def set_payment_status(wallet_address, status="false"):
    """
    Sets the payment status for a given wallet address in Redis with an expiration time.

    Args:
        wallet_address (str): The wallet address to which the status should be associated.
        status (str): The payment status to set, defaults to "false".
    """
    await app.redis.set(f"payment_confirmed_{wallet_address}", status, ex=60*10)


async def get_payment_status(wallet_address):
    """
    Retrieves the payment status for a given wallet address from Redis.

    Args:
        wallet_address (str): The wallet address for which to retrieve the payment status.

    Returns:
        str: The payment status.
    """
    return await app.redis.get(f"payment_confirmed_{wallet_address}")


async def set_payment_start_time(wallet_address):
    """
    Sets the payment start time for a given wallet address in Redis.

    Args:
        wallet_address (str): The wallet address for which to set the payment start time.
    """
    await app.redis.set(f"payment_start_time_{wallet_address}", datetime.now().timestamp())


async def get_payment_start_time(wallet_address):
    """
    Retrieves the payment start time for a given wallet address from Redis.

    Args:
        wallet_address (str): The wallet address for which to retrieve the payment start time.
    """
    timestamp = await app.redis.get(f"payment_start_time_{wallet_address}")
    if timestamp is not None:
        return datetime.fromtimestamp(float(timestamp))
    return None


async def set_email_in_redis(username, email):
    """
    Stores an email address associated with a discord username in Redis.

    Args:
        username (str): The discord username associated with the email.
        email (str): The email address to store.
    """
    await app.redis.set(f"email_{username}", email)


async def get_email_from_redis(username):
    """
    Retrieves an email address associated with a discord username from Redis.

    Args:
        username (str): The discord username associated with the email.
    """
    email = await app.redis.get(f"email_{username}")
    if email is not None:
        return email.decode('utf-8')
    return None


@app.route('/')
async def index():
    """
    Renders the main page of the application.

    Returns:
        Response: The rendered 'plan.html' template.
    """
    return await render_template('plan.html')


@app.route('/choose_plan', methods=['POST'])
async def choose_plan():
    """
    Handles the plan selection and stores the selected plan in the session.

    Returns:
        Response: A redirect to the payment page.
    """
    form_data = await request.form
    session['plan'] = form_data['plan']
    return redirect(url_for('payment'))


@app.route('/check_payment_status')
async def check_payment_status():
    """
    Checks and returns the payment status for the current session's wallet address.

    Returns:
        json: A JSON object with payment confirmation status, timeout status, and error messages if any.
    """
    wallet_address = session.get('wallet_address')

    payment_confirmed = await get_payment_status(wallet_address)

    await set_payment_start_time(wallet_address)
    payment_start_time = await get_payment_start_time(wallet_address)


    if payment_confirmed == b'true':
        return jsonify(payment_confirmed=True, payment_timeout=False)

    if not payment_start_time:
        return jsonify(payment_confirmed=False, payment_timeout=True, error="Payment session not started")

    elapsed_time = datetime.now() - payment_start_time
    if elapsed_time.total_seconds() > 10 * 60:
        return jsonify(payment_confirmed=False, payment_timeout=True)

    return jsonify(payment_confirmed=False, payment_timeout=False)


async def payment_check_coroutine(wallet_address, expected_amount, token, network, username):
    """
    Coroutine that continuously checks for payment confirmation within a specified time frame.

    Args:
        wallet_address (str): The wallet address for which to check the payment.
        expected_amount (float): The expected amount of payment.
        token (str): The token type for the payment.
        network (str): The network on which the payment is made.
        username (str): The username associated with the payment.
    """
    logger.info("The balance check coroutine has started.")
    payment = Payments()
    end_time = asyncio.get_event_loop().time() + 10 * 60
    try:
        while asyncio.get_event_loop().time() < end_time:
            logger.info(f"Checking payment at {asyncio.get_event_loop().time()}")
            success, _ = await payment.start_payment_session(expected_amount, wallet_address, token, network)
            logger.info(f"Check result: {success}, time: {asyncio.get_event_loop().time()}")
            if success:
                await set_payment_status(wallet_address, "true")
                logger.info("Payment confirmed")

                email = await get_email_from_redis(username)
                if email:
                    logger.info(f"Sending message to {email}")
                    recipient_email = email
                    subject = "10KDROP PAYMENT"
                    body = f"TEXT"
                    await send_message(recipient_email, subject, body)
                else:
                    logger.info("Cant get email address")

                logger.info(f"Adding discord role")
                formatted_username = username.split("#")[0]
                await assign_role_to_user(ds_token, guild_id, formatted_username, role_name)

                break
            await asyncio.sleep(2)
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        pass


@app.route('/email', methods=['POST'])
async def save_email():
    """
    Saves the user's email to Redis based on the current session's username.
    """
    data = await request.get_json()
    email = data['email']
    username = session.get('username')
    await set_email_in_redis(username, email)
    return jsonify(1)


@app.route('/payment', methods=['GET', 'POST'])
async def payment():
    """
    Handles the payment process. If the method is POST, it processes the payment data,
    generates a wallet, and initiates a payment check coroutine.
    If the method is GET, it renders the payment template.

    Returns:
        Response: Either a JSON response with payment details on POST or a rendered payment template on GET.
    """
    if request.method == 'POST':
        data = await request.get_json()
        token = data['token']
        network = data['network']

        wallet_address, private_key, mnemonic = await Payments.generate_wallet()
        session['wallet_address'] = wallet_address

        # TODO SAVING PK AND MNEMONIC TO MONGODB
        # session['private_key'] = private_key
        # session['mnemonic'] = mnemonic

        username = session['username']

        expected_amount = await Helper.getPlanPrice(plan_name=session['plan'], token=token)
        await set_payment_status(wallet_address, "false")

        asyncio.create_task(payment_check_coroutine(wallet_address, expected_amount, token, network, username))

        return jsonify(wallet_address=wallet_address, amount=expected_amount, token=token.upper())
    else:
        if 'access_token' not in session:
            return await render_template('payment.html')
        else:
            return await render_template('payment.html', session=session)


@app.route('/login/discord', methods=['POST'])
def discord_login():
    """
    Initiates the Discord OAuth2 login process by redirecting to the Discord OAuth2 URL.
    """
    return redirect(DISCORD_OAUTH2_URL)


@app.route('/oauth2/callback')
async def discord_oauth_callback():
    """
    Handles the OAuth2 callback from Discord. Exchanges the code for an access token and
    retrieves the user's Discord information to store in the session.

    Returns:
        Response: A redirect to the payment route on success or an error message on failure.
    """
    code = request.args.get('code')
    token_exchange_url = 'https://discord.com/api/oauth2/token'
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_exchange_url, data=token_data, headers=headers)
        if token_response.status_code == 200:
            token_json = token_response.json()
            access_token = token_json['access_token']
            session['access_token'] = access_token

            user_info_response = await client.get(
                'https://discord.com/api/v9/users/@me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                session['user_id'] = user_info['id']
                session['username'] = user_info['username'] + '#' + user_info['discriminator']

                return redirect(url_for('payment'))
            else:
                return "Failed to retrieve Discord user information.", 400
        else:
            return "Failed to authenticate via Discord.", 400


if __name__ == '__main__':
    app.run(debug=True)