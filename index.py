import asyncio
import os
import httpx
import aioredis

from datetime import datetime
from quart import Quart, render_template, request, redirect, url_for, session, jsonify
from payments import Payments
from utils import Helper
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, REDIS_HOST, REDIS_PORT, REDIS_PASSWD

app = Quart(__name__)

app.secret_key = os.urandom(16)

DISCORD_OAUTH2_URL = (
    f'https://discord.com/api/oauth2/authorize'
    f'?client_id={CLIENT_ID}'
    f'&redirect_uri={REDIRECT_URI}'
    f'&response_type=code'
    f'&scope={SCOPE}'
)


@app.before_serving
async def startup():
    app.redis = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        password=REDIS_PASSWD,
        encoding='utf-8'
    )


@app.after_serving
async def cleanup():
    await app.redis.close()


async def set_payment_status(wallet_address, status="false"):
    await app.redis.set(f"payment_confirmed_{wallet_address}", status, ex=60*10)


async def get_payment_status(wallet_address):
    return await app.redis.get(f"payment_confirmed_{wallet_address}")


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/choose_plan', methods=['POST'])
async def choose_plan():
    form_data = await request.form
    session['plan'] = form_data['plan']
    return redirect(url_for('payment'))


async def set_payment_start_time(wallet_address):
    await app.redis.set(f"payment_start_time_{wallet_address}", datetime.now().timestamp())


async def get_payment_start_time(wallet_address):
    timestamp = await app.redis.get(f"payment_start_time_{wallet_address}")
    if timestamp is not None:
        return datetime.fromtimestamp(float(timestamp))
    return None



@app.route('/check_payment_status')
async def check_payment_status():
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


async def payment_check_coroutine(wallet_address, expected_amount, token, network):
    print("Запущена корутина проверки баланса")
    payment = Payments()
    end_time = asyncio.get_event_loop().time() + 10 * 60
    try:
        while asyncio.get_event_loop().time() < end_time:
            print(f"Проверка платежа в {asyncio.get_event_loop().time()}")
            success, _ = await payment.start_payment_session(expected_amount, wallet_address, token, network)
            print(f"Результат проверки: {success}, время: {asyncio.get_event_loop().time()}")
            if success:
                await set_payment_status(wallet_address, "true")
                print("Платеж подтвержден")
                break
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


@app.route('/payment', methods=['GET', 'POST'])
async def payment():
    if request.method == 'POST':
        data = await request.get_json()
        token = data['token']
        network = data['network']

        wallet_address, private_key, mnemonic = await Payments.generate_wallet()
        session['wallet_address'] = wallet_address
        #session['private_key'] = private_key
        #session['mnemonic'] = mnemonic

        expected_amount = await Helper.getPlanPrice(plan_name=session['plan'], token=token)
        await set_payment_status(wallet_address, "false")

        asyncio.create_task(payment_check_coroutine(wallet_address, expected_amount, token, network))

        return jsonify(wallet_address=wallet_address, amount=expected_amount, token=token.upper())
    else:
        if 'access_token' not in session:
            return await render_template('payment.html')
        else:
            return await render_template('payment.html', session=session)


@app.route('/user_details', methods=['GET', 'POST'])
async def user_details():
    if request.method == 'POST':
        return redirect(url_for('user_details'))
    return await render_template('user_details.html')


@app.route('/login/discord', methods=['POST'])
def discord_login():
    return redirect(DISCORD_OAUTH2_URL)


@app.route('/oauth2/callback')
async def discord_oauth_callback():
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
                return "Не удалось получить информацию о пользователе Discord.", 400
        else:
            return "Не удалось аутентифицироваться через Discord.", 400


if __name__ == '__main__':
    app.run(debug=True)