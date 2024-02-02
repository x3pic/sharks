import asyncio
import base64
import copy
import json
import multiprocessing
import pickle
import queue
import random
import re
import threading
import time
import timeit
from collections import deque
from datetime import datetime
from threading import Thread
from jsonrpcclient import request, parse, Ok
import requests
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from solders.signature import Signature

from create_close_account import get_token_account,fetch_pool_keys, get_token_account, make_swap_instruction, fetch_pool_keys, sell_get_token_account,get_token_account, make_swap_instruction
import requests
from solana.rpc.commitment import Commitment
from solana.rpc.core import RPCException
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.client import Token
from spl.token.core import _TokenCore
from spl.token.instructions import CloseAccountParams, close_account
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Application, filters, CallbackQueryHandler, JobQueue

import solana
#mimic
key = "6739060490:AAHxintguEjcJpwpj28b9DWIGZhJrrNtF2g"  # Replace with your token
username = "@SharkshooterDemo_Bot"  # Replace with your bot's username



all_pool_keys = list()
pool_key_ids = set()
proxy_index = 0
manual_update = False


pickle_enabled = True

class MyQueue:
    def __init__(self, maxsize):
        self.queue = deque(maxlen=maxsize)

    def put(self, item):
        if len(self.queue) >= self.queue.maxlen:
            self.queue.popleft()  # Remove the oldest item
        self.queue.append(item)

    def get(self):
        if len(self.queue) == 0:
            raise IndexError("get from an empty queue")
        return self.queue.popleft()

    def includes(self, elem):
        return elem in self.queue

private_keys = {
}

statuses = {
}

amounts = {
}

cas = {
}

minumin_liqs = {
}

maximum_liqs = {
}

cache = {
}

prices_cache = {
}

token_supply_cache = {
}

toke_info_cache = {
}

limit_orders = {
}

snipes = {
}

snipe_limit_orders = {
}

update_context = {
}

mint_2_liquidity_delays = {
}

entry_delays = {
}

pool_creation_timestamps = {
}

require_socials = {
}

unparsed_transactions = queue.Queue()

my_queue = MyQueue(maxsize=2000)

async def get_token_symbol_async(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    # return pair with the most volume

    return max(pairs, key=lambda x: x["volume"]["h24"])["baseToken"]["symbol"]

def get_token_largest_accounts(token_mint_address):
    # URL of the Solana RPC server (replace with actual URL)
    url = random.choice(urls)

    # Prepare the data for the POST request
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenLargestAccounts",
        "params": [token_mint_address]
    }

    # Send the request and get the response
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()['result']['value']
    else:
        return "Error: Unable to fetch data from the Solana RPC server"


def get_token_supply(address):
    response = requests.post(random.choice(urls),
                             json=request("getTokenSupply", params=([address])))
    parsed = parse(response.json())
    if isinstance(parsed, Ok):
        return parsed.result["value"]["uiAmount"]
    else:
        return -1


async def get_solana_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    sol_price = data.get('solana', {}).get('usd')
    if sol_price:
        return sol_price
    else:
        return -1

def get_solana_price_sync():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    sol_price = data.get('solana', {}).get('usd')
    if sol_price:
        return sol_price
    else:
        return -1

def get_token_symbol(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    try:
        # return pair with the most volume
        return max(pairs, key=lambda x: x["volume"]["h24"])["baseToken"]["symbol"]
    except:
        return address

async def get_token_info(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    try:
        # return pair with the most volume
        return max(pairs, key=lambda x: x["volume"]["h24"])
    except:
        return None

def get_token_info_sync(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    try:
        # return pair with the most volume
        return max(pairs, key=lambda x: x["volume"]["h24"])
    except Exception as e:
        print(e)
        return None

async def get_token_marketcap(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    # return pair with the most volume

    try:
        return max(pairs, key=lambda x: x["volume"]["h24"])["fdv"]
    except:
        return 0

def get_token_pool(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    # return pair with the most volume
    return max(pairs, key=lambda x: x["volume"]["h24"])

def get_token_marketcap_sync(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    # return pair with the most volume
    try:
        return max(pairs, key=lambda x: x["volume"]["h24"])["fdv"]
    except:
        return 0

def get_token_price_sync(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    # return pair with the most volume
    try:
        return max(pairs, key=lambda x: x["volume"]["h24"])["priceUsd"]
    except:
        return 0

async def get_token_price(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=fXDTNUQjLY2Yn9dEhQWl4BNEGaQRwO7GGROoCyQlUAc-1703815807-1-AYqK669ZilAuLs6pCeIh7D25LTGZDMc4/DcwtaTqkMx/9gItgVDcGEy9LpHsDbTqA5DEb5AjEsQPTGyTvEPrTfCDz982t0j1VOiHkVET5ttX'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pairs = json.loads(response.text)["pairs"]

    # return pair with the most volume
    try:
        return max(pairs, key=lambda x: x["volume"]["h24"])["priceUsd"]
    except:
        return 0

# Function to create a menu with 3 buttons
def get_sniper_menu():
    keyboard = [
        [
            InlineKeyboardButton("📈BUY %", callback_data='buy_button'),
            InlineKeyboardButton("🦈SNIPE!", callback_data='snipe_button'),
            InlineKeyboardButton("SELL %📉", callback_data='sell_button'),
         ],
        [
            #InlineKeyboardButton("🤩Set take-profit", callback_data='tp_sell_button'),
            #InlineKeyboardButton("😥Set stop-loss", callback_data='sl_sell_button'),
            InlineKeyboardButton("🤩Set take-profit", callback_data='coming_soon'),
            InlineKeyboardButton("😥Set stop-loss", callback_data='coming_soon'),
        ],
        [
            InlineKeyboardButton("🔫🧮Set amount", callback_data='set_amount'),
            InlineKeyboardButton("🔫🤏Set min liquidity", callback_data='set_min_liquidity'),
            InlineKeyboardButton("🔫👐Set max liquidity", callback_data='set_max_liquidity'),

        ],
        [
            InlineKeyboardButton("🔫⏳️Set delay (mint2LP)", callback_data='set_mint_2_lp_delay'),
            InlineKeyboardButton("🔫⏳️Set entry delay", callback_data='set_entry_delay'),
        ],
        [
            InlineKeyboardButton("🔫📫Set CA", callback_data='set_ca'),
        ],
        [
            InlineKeyboardButton("🙅Cancel...", callback_data='cancel_menu'),
        ],
        [
            InlineKeyboardButton("Tip 0.01 SOL", callback_data='donate'),
            InlineKeyboardButton("🔑Export key", callback_data='export_key'),
        ],
        [
            InlineKeyboardButton("🔄REFRESH🔄", callback_data='refresh'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def get_cancel_menu():
    keyboard = [
        [
            InlineKeyboardButton("1🦈Cancel snipe", callback_data='cancel_snipe'),
            InlineKeyboardButton("🤩Cancel limit orders", callback_data='cancel_limit'),
        ],
        [
            InlineKeyboardButton("🦈Cancel all snipes", callback_data='cancel_all_snipes'),
            InlineKeyboardButton("🤖Cancel auto TP", callback_data='cancel_snipe_limit'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def button_callback(update: Update, context):
    query = update.callback_query
    #await query.answer()  # Answer callback query
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    update_context[user_id] = (update, context)

    statuses[user_id] = ""

    #delete all previous messages
    #await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id-1)
    if query.data == 'snipe_menu':
        statuses[user_id] = ""
        await show_snipe_menu(update,context)
        return
    elif query.data == 'set_ca':
        await set_ca(update, context)
        return
    elif query.data == "refresh":
        statuses[user_id] = ""
        await refresh(update, context)
        return
    elif query.data == "buy_button":
        await buy_button(update, context)
        return
    elif query.data == "sell_button":
        await sell_button(update, context)
        return
    elif query.data == "export_key":
        await export_key(update, context)
        return
    elif query.data == "withdraw":
        await withdraw(update, context)
        return
    elif query.data == "cancel_snipe_limit":
        await cancel_snipe_limit(update, context)
        return
    elif query.data == "set_mint_2_lp_delay":
        await set_mint_2_lp_delay(update,context)
        return
    elif query.data == "set_entry_delay":
        await set_entry_delay(update,context)
        return
    elif query.data == "donate":
        await donate_sol(update, context)
        return
    elif query.data == "cancel_menu":
        chat_id = update.effective_message.chat_id
        await context.bot.send_message(chat_id=chat_id,
                                       text="What do you want to cancel?",
                                       reply_markup=get_cancel_menu(),
                                       parse_mode="markdown",
                                       disable_web_page_preview=True)
        return

    try:
        key = private_keys[user_id]
    except:
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"Send /start to generate an address.")
        return
    keypair = Keypair.from_seed(key)
    public_key = keypair.pubkey()

    soltama_balance = await get_token_balance(token_address=soltama_address, wallet_address=str(public_key))

    whitelist = [
        "1909810080",
        "6631784900",
        "999379594",
        "6157896468",
        "6428674695",
        "876405598",
        "6964242004",
        "524236112", #miha
        "1686010216",
        "6030748198",
        "6257787662",
        "5636755487",
        "5327213521",
        "1901010226",
        "1597169345",
        "1861781610",
        "506171847",
        "6343801318",
        "621199139"
    ]

    if soltama_balance < 7500000 and str(user_id) not in whitelist:
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"You need to have at least 7500000 SHARKS in your wallet to use the bot. You currently have {soltama_balance} SHARKS.")
        return

    # Determine which function to call based on the button pressed

    if query.data == 'set_amount':
        await set_amount(update, context)
    elif query.data == 'set_min_liquidity':
        await set_min_liquidity(update, context)
    elif query.data == 'set_max_liquidity':
        await set_max_liquidity(update, context)
    elif query.data == "coming_soon":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Coming soon! ")
    elif query.data == "tp_sell_button":
        await tp_sell_button(update, context)
    elif query.data == "sl_sell_button":
        await sl_sell_button(update, context)
    elif query.data == "cancel_limit":
        await cancel_limit(update, context)
    elif query.data == "cancel_snipe":
        await cancel_snipe(update, context)
    elif query.data == "cancel_all_snipes":
        await cancel_all_snipes(update, context)
    elif query.data == "snipe_button":
        await snipe_button(update, context)
    elif query.data == "token_balances":
        await token_balances(update, context)

async def export_key(update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    key = private_keys[user_id]

    keypair = Keypair.from_seed(key)


    await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"Your private key is:")
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"`{Keypair.from_seed(key).to_json()}`", parse_mode="Markdown")

async def get_token_balances(user_id):
    from spl.token.constants import TOKEN_PROGRAM_ID

    private_key = private_keys[user_id]

    keypair = Keypair.from_seed(private_key)

    result_json = random.choice(clients).get_token_accounts_by_owner(keypair.pubkey(), TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)).to_json()
    result = json.loads(result_json)

    if result['result']['value']:
        token_accounts = result['result']['value']
        tokens = []

        for account in token_accounts:
            # Get the mint address and balance
            print("xxxxxaccount", account)
            mint_address = account['pubkey']
            balance = await get_token_balance(mint_address, str(keypair.pubkey()))
            try:
                symbol = await get_token_symbol_async(mint_address)
            except:
                symbol = mint_address

            # Append the token details to the list
            tokens.append({
                'mint_address': mint_address,
                'balance': balance,
                'symbol': symbol
            })

        return tokens

    else:
        return []



async def token_balances(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    balances = await get_token_balances(user_id)
    print("xxxxxbalances", balances)
    text = ""
    for balance in balances:
        text += f"{balance['symbol']}: {balance['balance']}\n"

    await context.bot.send_message(chat_id=update.effective_message.chat_id, text=text)

async def cancel_limit(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    status = statuses.get(user_id, "")
    if status == "":
        try:
            del limit_orders[user_id]
        except:
            await refresh(update, context)
            return
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Order cancelled!")
        await refresh(update, context)
        pickle.dump(limit_orders, open("limit_orders.pkl", "wb"))
        return
        #statuses[user_id] = "cancel_limit"
        #await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter the number of the order you wish to cancel:")

    elif status == "cancel_limit":
        statuses[user_id] = ""

        try:
            id = int(update.effective_message.text)
            del limit_orders[user_id]
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Order cancelled!")
            await refresh(update, context)
            pickle.dump(limit_orders, open("limit_orders.pkl", "wb"))
        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid order number!")
            return

        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Order cancelled!")

async def cancel_snipe_limit(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    status = statuses.get(user_id, "")
    if status == "":
        statuses[user_id] = "cancel_snipe_limit"
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter the number of the order you wish to cancel:")

    elif status == "cancel_snipe_limit":
        statuses[user_id] = ""

        try:
            id = int(update.effective_message.text)
            orders = snipe_limit_orders[user_id]
            for order in orders:
                if order["id"] == id:
                    orders.remove(order)

                    for index, order in enumerate(orders):
                        order["id"] = index + 1

                    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Order cancelled!")
                    await refresh(update, context)
                    pickle.dump(snipe_limit_orders, open("snipe_limits.pkl", "wb"))
                    return
        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid order number!")
            return

        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Order cancelled!")

async def cancel_all_snipes(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    snipes[user_id] = []
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="All snipes cancelled!")
    await refresh(update, context)

async def cancel_snipe(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    status = statuses.get(user_id, "")
    if status == "":
        statuses[user_id] = "cancel_snipe"
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter the number of the snipe you wish to cancel:")

    elif status == "cancel_snipe":
        statuses[user_id] = ""

        try:
            id = int(update.effective_message.text)
            orders = snipes[user_id]
            for order in orders:
                if order["id"] == id:
                    orders.remove(order)

                    for index, order in enumerate(orders):
                        order["id"] = index+1


                    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Snipe cancelled!")
                    await refresh(update, context)
                    pickle.dump(limit_orders, open("snipes.pkl", "wb"))
                    return
        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid snipe number!")
            return

        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Snipe cancelled!")

async def refresh(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = ""
    try:
        await context.bot.delete_message(chat_id=update.effective_message.chat_id, message_id=update.effective_message.message_id)
    except:
        pass
    await show_snipe_menu(update, context)

async def set_amount(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "set_amount"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter amount:")


async def set_min_liquidity(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "set_min_liquidity"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter min liquidity:")

async def set_max_liquidity(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "set_max_liquidity"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter max liquidity:")

async def set_entry_delay(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "set_entry_delay"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter entry delay in seconds (greater than 90 or 0):")

async def set_mint_2_lp_delay(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "set_mint_2_lp_delay"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter entry delay in seconds (greater than 90 or 0):")

async def set_ca(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "set_ca"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter CA (x for any):")

async def withdraw(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    statuses[user_id] = "withdraw"
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Enter your address:")

async def handle_message(update: Update, context):
    user_id = str(update.message.from_user.id)
    status = statuses.get(user_id, "")

    if status == "cancel_snipe_limit":
        await cancel_snipe_limit(update, context)
    elif status == "set_amount":
        try:
            amount = float(update.message.text)
            statuses[user_id] = ""
            #print("AAMOUNT SET, ", amount)
            amounts[user_id] = amount
            #delete last 3 messages
            try:
                await context.bot.delete_message(chat_id=update.effective_message.chat_id, message_id=update.effective_message.message_id-2)
            except:
                pass
            await refresh(update, context)
            #await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"Amount set to {amount}")
        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid amount")
    elif status == "set_ca":
        address = update.message.text
        if len(address) < 10:
            address = address.lower()
        statuses[user_id] = ""
        cas[user_id] = address
        try:
            await context.bot.delete_message(chat_id=update.effective_message.chat_id,message_id=update.effective_message.message_id - 2)
        except:
            pass
        await refresh(update, context)

    elif status == "set_min_liquidity":
        statuses[user_id] = ""
        try:
            id = float(update.message.text)
            minumin_liqs[user_id] = id
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Min liquidity set!")
            await refresh(update, context)
            return

        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid number!")
            return

    elif status == "set_max_liquidity":
        statuses[user_id] = ""
        try:
            id = float(update.message.text)
            maximum_liqs[user_id] = id
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Max liquidity set!")
            await refresh(update, context)
            return

        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid number!")
            return

    elif status == "set_mint_2_lp_delay":
        statuses[user_id] = ""
        try:
            id = int(update.message.text)

            if id != 0 and id < 90:
                await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Entry delay must be at least 90 seconds!")
                return

            mint_2_liquidity_delays[user_id] = id

            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Entry delay set!")
            await refresh(update, context)
            return

        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid number!")
            return

    elif status == "set_entry_delay":
        statuses[user_id] = ""
        try:
            id = int(update.message.text)

            if id != 0 and id < 90:
                await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Entry delay must be at least 90 seconds!")
                return

            entry_delays[user_id] = id

            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Entry delay set!")
            await refresh(update, context)
            return

        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid number!")
            return

    elif status == "withdraw":
        address = update.message.text.strip()
        statuses[user_id] = ""
        await withdraw_sol(update, context, address)
        #try:
        #
        #except Exception as e:
        #    print(e)
        #    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Error")

    elif "tp_sell" in status:
        await tp_sell_button(update, context)

    elif "sl_sell" in status:
        await sl_sell_button(update, context)

    elif "buy" in status:
        await buy_button(update, context)

    elif "sell" in status:
        await sell_button(update, context)

    elif status == "cancel_limit":
        await cancel_limit(update, context)

    elif status == "cancel_snipe":
        await cancel_snipe(update, context)

    elif status == "set_min_liquidity":
        await set_min_liquidity(update, context)

    elif status == "snipe_amount":
        await snipe_button(update, context)

async def sl_sell_button(update: Update, context):
    percent = 0
    try:
        user_id = str(update.message.from_user.id)
        percent = int(update.message.text.replace("%", "").strip())
    except:
        user_id = str(update.callback_query.from_user.id)

    ca = cas.get(user_id, "")
    if ca == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="CA not set!")
        return

    status = statuses.get(user_id, "")
    private_key = private_keys[user_id]
    public_key = str(Keypair.from_seed(private_key).pubkey())
    balance = await get_token_balance(ca, public_key, lamports=True)
    amount = balance * (percent / 100)

    if status == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                       text="Send the amount you wish to sell (0 - 100 %):")
        statuses[user_id] = "sl_sell0"
    elif status == "sl_sell0":
        cache[user_id] = {"amount": amount}
        await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                       text="Sell if the marketcap is lower than x USD:")
        statuses[user_id] = "sl_sell1"
    elif status == "sl_sell1":
        cache[user_id]["market_cap"] = float(update.message.text)
        asyncio.create_task(
            take_profit_task(context, update, user_id, cache[user_id]["amount"], cache[user_id]["market_cap"], ca, stop_loss=True))
        del cache[user_id]
        await asyncio.sleep(1)
        await refresh(update, context)

async def snipe_button(update: Update, context):


    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)



    ca = cas.get(user_id, "")
    status = statuses.get(user_id, "")



    if ca.lower() == "x" and status == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="How many times?")
        statuses[user_id] = "snipe_amount"
        return

    if ca == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="CA not set!")
        return
    amount = amounts.get(user_id, 0)
    if amount == 0:
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Amount not set!")
        return
    min_liq = minumin_liqs.get(user_id, 0)
    if min_liq == 0:
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Minimum liquidity not set!")
        return
    max_liq = maximum_liqs.get(user_id, 0)
    if max_liq == 0:
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Maximum liquidity not set!")
        return

    count = 1
    if status == "snipe_amount":
        try:
            count = int(update.message.text)
            if count > 10:
                count = 5
        except:
            await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid amount")
            return

    statuses[user_id] = ""

    for i in range(count):
        asyncio.create_task(snipe_task(context, update, user_id, amount, ca, min_liq, max_liq))
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Snipe task started!")
    await asyncio.sleep(1)
    await refresh(update, context)

async def snipe_task(context, update, user_id, amount, token_address, min_liq, max_liq):

    existing = snipes.get(user_id, None)
    if existing is not None:
        snipe_id = len(existing)
    else:
        snipe_id = 0

    #unix timestamp
    timestamp = int(time.time())

    snipe = {
        "amount": amount,
        "min_liq": min_liq,
        "max_liq": max_liq,
        "token_address": token_address,
        "user_id": user_id,
        "id": snipe_id+1,
        "snipe_status": "pending",
        "timestamp": timestamp,
    }

    if existing is not None:
        snipes[user_id].append(snipe)
    else:
        snipes[user_id] = [snipe]

    if pickle_enabled:
        pickle.dump(snipes, open("snipes.pkl", "wb"))

async def tp_sell_button(update: Update, context):
    percent = 0
    try:
        user_id = str(update.message.from_user.id)
        percent = int(update.message.text.replace("%", "").strip())
    except:
        user_id = str(update.callback_query.from_user.id)

    ca = cas.get(user_id, "")
    if ca == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="CA not set!")
        return

    status = statuses.get(user_id, "")

    print(status)


    if status == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                       text="Send the amount you wish to sell (0 - 100 %):")
        statuses[user_id] = "tp_sell0"
    elif status == "tp_sell0":
        private_key = private_keys[user_id]
        public_key = str(Keypair.from_seed(private_key).pubkey())
        balance = await get_token_balance(ca, public_key, lamports=True)
        amount = balance * (percent / 100)
        cache[user_id] = {"amount": amount}
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Sell if the price is higher than x USD:")
        statuses[user_id] = "tp_sell1"
    elif status == "tp_sell1":
        cache[user_id]["market_cap"] = float(update.message.text.replace("%", "").strip())
        asyncio.create_task(take_profit_task(context, update, user_id, cache[user_id]["amount"], cache[user_id]["market_cap"], ca))
        del cache[user_id]
        await asyncio.sleep(1)
        await refresh(update, context)


async def take_profit_task(context, update, user_id, amount, target_price, token_address, stop_loss=False):

    ca = token_address
    if amount == -1:
        key = private_keys[user_id]
        public_key = str(Keypair.from_seed(key).pubkey())
        token_balance = await get_token_balance(ca, public_key, lamports=True)

    existing = limit_orders.get(user_id, None)
    if existing is None:
        id = 0
    else:
        id = len(existing)

    try:

        info = {
            "user_id": user_id,
            "amount": round(amount, 4),
            "target_price": target_price,
            "token": await get_token_symbol_async(ca),
            "stop_loss": stop_loss,
            "id": id+1,
            "address": ca,
        }
    except:
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Invalid token address!")
        return

    if limit_orders.get(user_id, None) is None:
        limit_orders[user_id] = [info]
    else:
        limit_orders[user_id].append(info)

    pickle.dump(limit_orders, open("limit_orders.pkl", "wb"))



async def buy_button(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)

    solana_client = random.choice(clients)



    status = statuses.get(user_id, "")

    if status == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Send the token address:")
        statuses[user_id] = "buy1"
    elif status == "buy1":
        address = update.message.text.strip()
        cache[user_id] = address
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"Send the amount you wish to buy (0 - 100 %):")
        statuses[user_id] = "buy2"
    elif status == "buy2":
        address = cache[user_id]
        percent = int(update.message.text.replace("%", "").strip())
        private_key = private_keys[user_id]
        public_key = Keypair.from_seed(private_key).pubkey()

        balance = await get_sol_balance(update, context, public_key)
        amount = balance * (percent / 100)
        private_key = private_keys[user_id]
        pubkey = Keypair.from_seed(private_key)
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"Transaction for {amount} SOL sent")
        statuses[user_id] = ""

        event_loop = asyncio.get_event_loop()
        event_loop.create_task(buy(solana_client, address, pubkey, amount=amount, user_id=user_id))


async def sell_button(update: Update, context):
    try:
        user_id = str(update.message.from_user.id)
    except Exception as e:
        print(e)
        user_id = str(update.callback_query.from_user.id)


    status = statuses.get(user_id, "")

    solana_client = random.choice(clients)

    if status == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Send the token address:")
        statuses[user_id] = "sell1"
    elif status == "sell1":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Send the amount you wish to sell (0 - 100 %):")
        statuses[user_id] = "sell2"
        address = update.message.text.strip()
        cache[user_id] = address
    elif status == "sell2":
        percent = int(update.message.text.replace("%", "").strip())
        address = cache[user_id]
        private_key = private_keys[user_id]
        public_key = str(Keypair.from_seed(private_key).pubkey())
        balance = await get_token_balance(address, public_key, lamports=True)
        amount = balance * (percent / 100)
        private_key = private_keys[user_id]
        keypair = Keypair.from_seed(private_key)
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text=f"Transaction for {amount} units sent...")
        statuses[user_id] = ""
        #print("SELLING" + str(amount) + str(address))
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(sell(solana_client, address, keypair, amount, user_id=user_id))


async def get_token_balance(token_address, wallet_address, lamports=False):
    headers = {"accept": "application/json", "content-type": "application/json"}

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"mint": token_address},
            {"encoding": "jsonParsed"},
        ],
    }
    print("PARAMS", payload["params"])
    rpc_url = random.choice(urls)
    response = requests.post(rpc_url, json=payload, headers=headers)
    print(response.json())
    if not lamports:
        try:
            amount = response.json()["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
        except:
            amount = 0
    else:
        try:
            amount = response.json()["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"]
        except:
            amount = 0
    print("AMOUNT", amount)
    return float(amount)

async def get_sol_balance(update: Update, context, pubkey: Pubkey, lamports=False):

    solana_client = random.choice(clients)
    balance = solana_client.get_balance(pubkey).to_json()

    value = json.loads(balance)['result']['value']


    if not lamports:
        value = value / 1000000000

    return value

def get_pool_keys_from_transaction(transaction, token_address):
    account_keys = transaction['result']['transaction']['message']['accountKeys']

    source = Pubkey.from_string(account_keys[0])
    #get source transactions
    source_transactions_json = random.choice(clients).get_signatures_for_address(source).to_json()
    source_transactions = json.loads(source_transactions_json)['result']


    pool_keys = None

    flag = False
    for signature in source_transactions:
        if flag:
            #print(signature['signature'])
            tx_json = random.choice(clients).get_transaction(Signature.from_string(signature['signature']), max_supported_transaction_version=0).to_json()
            tx = json.loads(tx_json)
            transaction_keys = tx['result']['transaction']['message']['accountKeys']
            #print(len(transaction_keys))
            if len(transaction_keys) == 13 or len(transaction_keys) == 12:
                #print(tx)
                pool_keys = tx['result']['transaction']['message']['accountKeys']

                pool_creation_timestamps[token_address] = tx['result']['blockTime']

                break
        if signature['signature'] == transaction['result']['transaction']['signatures'][0]:
            flag = True


    liq = calculate_liquidity_addition(transaction)
    keys = set(liq.keys())
    try:
        keys.remove(sol_address)
    except:
        return
    token_address = keys.pop()
    token_decimals = 0

    post_balances = transaction['result']['meta']['postTokenBalances']
    for bal in post_balances:
        if bal['mint'] == token_address:
            token_decimals = bal['uiTokenAmount']['decimals']


    return {
        'amm_id': Pubkey.from_string(account_keys[2]),
        'authority': Pubkey.from_string(account_keys[16]),
        'base_mint': Pubkey.from_string(account_keys[17]),
        'base_decimals': token_decimals,
        'quote_mint': Pubkey.from_string(account_keys[14]),
        'quote_decimals': 9,
        'lp_mint': Pubkey.from_string(account_keys[4]),
        'open_orders': Pubkey.from_string(account_keys[3]),
        'target_orders': Pubkey.from_string(account_keys[7]),
        'base_vault': Pubkey.from_string(account_keys[5]),
        'quote_vault': Pubkey.from_string(account_keys[6]),
        'market_id': Pubkey.from_string(account_keys[19]),
        'bids': Pubkey.from_string(pool_keys[6]),
        'asks': Pubkey.from_string(pool_keys[7]),
        'event_queue': Pubkey.from_string(pool_keys[4]),
        'market_base_vault': Pubkey.from_string(pool_keys[8]),
        'market_quote_vault': Pubkey.from_string(pool_keys[9]),
        'market_authority': Pubkey.from_string(pool_keys[2]),
    }

def get_metadata_from_IDO_signature(signature):
    try:
        ido_tx = Signature.from_string(signature)

        # get signer of ido tx
        ido_tx_info = client8.get_transaction(ido_tx, max_supported_transaction_version=0)
        signer = json.loads(ido_tx_info.to_json())['result']['transaction']['message']['accountKeys'][0]
        signer = Pubkey.from_string(signer)
        #print(signer)

        # get transactions from signer
        transactions_json = client8.get_signatures_for_address(signer).to_json()
        transactions = json.loads(transactions_json)['result']

        metadata_address = ""
        # iterate oldest to newest
        for _tx in transactions[::-1]:
            sig = Signature.from_string(_tx['signature'])
            tx = client8.get_transaction(sig, max_supported_transaction_version=0)
            keys = json.loads(tx.to_json())['result']['transaction']['message']['accountKeys']
            if metaplex_address in keys:
                deployment_keys = json.loads(tx.to_json())['result']['transaction']['message']['accountKeys']
                metadata_address = deployment_keys[3]
                break

        # metadata_address = "BmykbEAsHfj652tmiRPAbDouT7ToYLbYTtrcH5nXbx6u"

        info = client8.get_account_info(Pubkey.from_string(metadata_address))
        #print(info)

        data = json.loads(info.to_json())["result"]["value"]["data"][0]
        #print(data)

        # convert base64 bytes to string
        data = base64.b64decode(data)


        string = str(data)
        #print(string)
        url = ("https://" + string.split("https://")[1]).split("\\")[0]
        #print(url)
    except:
        #print("{}")
        return ""

    # get json from url
    response = requests.get(url)
    try:
        #return json
        #return response.json()
        #return json string
        return json.dumps(response.json())
    except:
        return "{}"

async def buy(solana_client, token_address, payer, amount=0, sol_amount=0, snipe=None, mint_2_liq_delay=0, entry_delay=0, transaction=None, min_liq=None, max_liq=None, user_id=None, take_profit=False, token_price=None):

    if snipe is not None:
        amount = snipe['amount']
        snipe_id = snipe['id']

        if entry_delay > 0:
            print("delaying for ", entry_delay, "seconds")
            await asyncio.sleep(entry_delay)
            solana_price = await get_solana_price()
            info = toke_info_cache.get(token_address, None)
            if info == None:
                info = await get_token_info(token_address)
                toke_info_cache[token_address] = info
            hour_minutes_seconds_string = datetime.now().strftime("%H:%M:%S")
            print(f"{token_address} {hour_minutes_seconds_string} info: ",info)
            if info == None:
                print(token_address, "Token not found")
                if snipe_id is not None:
                    user_snipes = snipes.get(user_id, [])
                    for snipe in user_snipes:
                        if snipe["id"] == snipe_id and snipe["token_address"] == "x":
                            snipe["snipe_status"] = "pending"
                return
            if info['liquidity']["quote"] <= min_liq or info['liquidity']["quote"] >= max_liq:
                print(token_address, "Not enough liquidity")
                if snipe_id is not None:
                    user_snipes = snipes.get(user_id, [])
                    for snipe in user_snipes:
                        if snipe["id"] == snipe_id and snipe["token_address"] == "x":
                            snipe["snipe_status"] = "pending"
                return
            token_price = await get_token_price(token_address)

    else:
        amount = amount
        snipe_id = None


    #payer = key pair
    try:
        mint = Pubkey.from_string(token_address)
    except:
        raise Exception("Invalid Token Address: " + token_address)
    LAMPORTS_PER_SOL = 1000000000

    try:
        symbol = await get_token_symbol_async(str(mint))
    except:
        symbol = "Unknown"

    count = 0

    try:

        print(f"BUY {symbol}...")

        if transaction is None:

            pook_keys = cached_pool_keys.get(str(mint), None)
            if pook_keys is None:
                pool_keys = fetch_pool_keys(str(mint))
                if pool_keys == "failed":
                    if user_id is not None:
                        update, context = update_context[user_id]
                        await context.bot.send_message(chat_id=update.effective_message.chat_id,text="Cant trade non-sniped tokens, please use another wallet")
                        return False
                    print(f"a|BUY Pool ERROR {symbol}", f"[Raydium]: Pool Key Not Found")
                    return False
        else:
            pool_keys = get_pool_keys_from_transaction(transaction, token_address)
            cached_pool_keys[str(mint)] = pool_keys

        pool_creation_timestamp = pool_creation_timestamps.get(token_address, 0)

        print(f"{user_id}-ACTUALLY CREATED", time.time() - pool_creation_timestamp)


        if user_id == "876405598":
            #write to file
            with open("pool_creation_timestamps.txt", "a") as f:
                f.write(f"{token_address},{time.time() - pool_creation_timestamp},{sol_amount}\n")
                f.close()


        #if pool created less than <delay> seconds ago, wait
        if pool_creation_timestamp > 0 and time.time() - pool_creation_timestamp < mint_2_liq_delay:
            if snipe_id is not None:
                user_snipes = snipes.get(user_id, [])
                for snipe in user_snipes:
                    if snipe["id"] == snipe_id and snipe["token_address"] == "x":
                        snipe["snipe_status"] = "pending"
            print(f"CANCELLED BUY {symbol}...", f"[Raydium]: Pool Created Less Than {mint_2_liq_delay} Seconds Ago")
            return False

        """
        Calculate amount
        """
        amount_in = int(amount * LAMPORTS_PER_SOL)
        # slippage = 0.1
        # lamports_amm = amount * LAMPORTS_PER_SOL
        # amount_in =  int(lamports_amm - (lamports_amm * (slippage/100)))

        error = False
        txnBool = True
        while txnBool:

            """Get swap token program id"""
            print("1. Get TOKEN_PROGRAM_ID...")
            accountProgramId = solana_client.get_account_info_json_parsed(mint)
            TOKEN_PROGRAM_ID = accountProgramId.value.owner

            """
            Set Mint Token accounts addresses
            """
            print("2. Get Mint Token accounts addresses...")
            swap_associated_token_address, swap_token_account_Instructions = get_token_account(solana_client,
                                                                                               payer.pubkey(), mint)

            """
            Create Wrap Sol Instructions
            """
            print("3. Create Wrap Sol Instructions...")
            balance_needed = Token.get_min_balance_rent_for_exempt_for_account(solana_client)
            WSOL_token_account, swap_tx, payer, Wsol_account_keyPair, opts, = _TokenCore._create_wrapped_native_account_args(
                TOKEN_PROGRAM_ID, payer.pubkey(), payer, amount_in,
                False, balance_needed, Commitment("confirmed"))
            """
            Create Swap Instructions
            """
            print("4. Create Swap Instructions...")
            instructions_swap = make_swap_instruction(amount_in,
                                                      WSOL_token_account,
                                                      swap_associated_token_address,
                                                      pool_keys,
                                                      mint,
                                                      solana_client,
                                                      payer
                                                      )

            print("5. Create Close Account Instructions...")
            params = CloseAccountParams(account=WSOL_token_account, dest=payer.pubkey(), owner=payer.pubkey(),
                                        program_id=TOKEN_PROGRAM_ID)
            closeAcc = (close_account(params))

            print("6. Add instructions to transaction...")
            if swap_token_account_Instructions != None:
                swap_tx.add(swap_token_account_Instructions)
            swap_tx.add(instructions_swap)
            swap_tx.add(closeAcc)

            try:
                print("7. Execute Transaction...")
                start_time = time.time()
                txn = solana_client.send_transaction(swap_tx, payer, Wsol_account_keyPair)
                txid_string_sig = txn.value

                print("8. Confirm transaction...", txid_string_sig)
                checkTxn = True
                while checkTxn:
                    try:
                        status = solana_client.get_transaction(txid_string_sig, "json")

                        FeesUsed = (status.value.transaction.meta.fee) / 1000000000



                        if status.value.transaction.meta.err == None:
                            print("[create_account] Transaction Success", txn.value)
                            print(f"[create_account] Transaction Fees: {FeesUsed:.10f} SOL")

                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(f"Execution time: {execution_time} seconds")

                            if snipe_id is not None:
                                user_snipes = snipes.get(user_id, [])
                                for snipe in user_snipes:
                                    if snipe["id"] == snipe_id:
                                        snipe["snipe_status"] = "success"
                                        snipe["snipe_tx"] = txn.value
                                        snipe["token_address"] = token_address
                                        if pickle_enabled:
                                            pickle.dump(snipes, open("snipes.pkl", "wb"))

                                        tx_json = status.to_json()
                                        tx = json.loads(tx_json)

                                        key = private_keys.get(user_id, None)
                                        if key is None:
                                            raise Exception("Private Key Not Found")
                                        keypair = Keypair.from_seed(key)
                                        owner = str(keypair.pubkey())
                                        print("owner address: ", owner)

                                        tokens_bought = 0
                                        uiAmount= 0
                                        post_balances = tx['result']['meta']['postTokenBalances']
                                        for post_balance in post_balances:
                                            if post_balance['owner'] == owner:
                                                tokens_bought = float(post_balance['uiTokenAmount']['amount'])
                                                uiAmount = float(post_balance['uiTokenAmount']['uiAmountString'])
                                                break

                                        print("tokens_bought: ", tokens_bought)

                                        # info = {
                                        #    "amount": amount,
                                        #    "profit": profit,
                                        #    "id": id + 1,
                                        #    "user_id": user_id,
                                        # }


                                        #write token address to file in new line
                                        with open("snipe_success.txt", "a") as f:
                                            f.write(token_address + "\n")

                                        #creat take profit order
                                        if take_profit:
                                            print("Take profit...")



                            if user_id is not None:
                                update, context = update_context[user_id]
                                await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                                               text=f"Transaction Success\n"
                                                                    f"`{token_address}`\n"
                                                                    f"[chart](https://dexscreener.com/solana/{token_address})", parse_mode="Markdown")


                            txnBool = False
                            checkTxn = False
                            #return txid_string_sig
                            return True

                        else:
                            if user_id is not None:
                                update, context = update_context[user_id]
                                await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                                               text="Transaction Failed\n")
                            print("Transaction Failed")
                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(f"Execution time: {execution_time} seconds")
                            checkTxn = False
                            return False

                    except Exception as e:
                        print(f"e|BUY ERROR {symbol}", f"[Raydium]: {e}")
                        print("Sleeping...", e)
                        await asyncio.sleep(1)
                        print("Retrying...")
                        count = count + 1
                        if count >= 70:
                            txnBool = False
                            checkTxn = False
                            if snipe_id is not None:
                                user_snipes = snipes.get(user_id, [])
                                for snipe in user_snipes:
                                    if snipe["id"] == snipe_id and snipe["token_address"] == "x":
                                        snipe["snipe_status"] = "pending"
                            return False

            except Exception as e:
                print(f"e|BUY Exception ERROR {symbol}", f"[Raydium]: {e}")
                print(f"Error: [{e}]...\nEnd...")
                txnBool = False
                if snipe_id is not None:
                    user_snipes = snipes.get(user_id, [])
                    for snipe in user_snipes:
                        if snipe["id"] == snipe_id:
                            snipe["snipe_status"] = "pending"
                return False
            await asyncio.sleep(1)
    except Exception as e:
        print("snipe error", e)
        if snipe_id is not None:
            user_snipes = snipes.get(user_id, [])
            for snipe in user_snipes:
                if snipe["id"] == snipe_id and snipe["token_address"] == "x":
                    snipe["snipe_status"] = "pending"

async def sell(solana_client, TOKEN_TO_SWAP_SELL, payer, amount_in, user_id=None, automatic=False, token_address="", order_seed=None):

    if TOKEN_TO_SWAP_SELL == "x":
        if user_id is not None:
            update, context = update_context[user_id]
            await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                           text="Invalid Token Address")
        return False

    try:
        token_symbol = await get_token_symbol_async(TOKEN_TO_SWAP_SELL)
    except:
        token_symbol = "unknown"

    print(f"SELL {TOKEN_TO_SWAP_SELL}...")


    mint = Pubkey.from_string(TOKEN_TO_SWAP_SELL)
    sol = Pubkey.from_string("So11111111111111111111111111111111111111112")

    """Get swap token program id"""
    print("1. Get TOKEN_PROGRAM_ID...")
    TOKEN_PROGRAM_ID = solana_client.get_account_info_json_parsed(mint).value.owner

    print("TOKEN_PROGRAM_ID", TOKEN_PROGRAM_ID)

    """Get Pool Keys"""
    print("2. Get Pool Keys...")

    pool_keys = cached_pool_keys.get(str(mint), None)
    if pool_keys is None:
        pool_keys = fetch_pool_keys(str(mint))
        if pool_keys == "failed":
            if user_id is not None:
                update, context = update_context[user_id]
                await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                               text="Cant trade non-sniped tokens, please use another wallet")
                return False
            print(f"a|Sell Pool ERROR {token_symbol}", f"[Raydium]: Pool Key Not Found")
            return False

    txnBool = True

    count = 0

    while txnBool:
        """Get Token Balance from wallet"""
        #print("3. Get oken Balance from wallet...")
        #amount_in = 0

        #balanceBool = True
        #while balanceBool:
        #    tokenPk = mint

        #    accountProgramId = solana_client.get_account_info_json_parsed(tokenPk)
        #    programid_of_token = accountProgramId.value.owner

        #    accounts = solana_client.get_token_accounts_by_owner_json_parsed(payer.pubkey(), TokenAccountOpts(
        #        program_id=programid_of_token)).value
        #    for account in accounts:
        #        mint_in_acc = account.account.data.parsed['info']['mint']
        #        if mint_in_acc == str(mint):
        #            amount_in = int(account.account.data.parsed['info']['tokenAmount']['amount'])
        #            print("3.1 Token Balance [Lamports]: ", amount_in)
        #            break
        #    if int(amount_in) > 0:
        #        balanceBool = False
        #    else:
        #        print("No Balance, Retrying...")
        #        time.sleep(2)

        """Get token accounts"""
        print("4. Get token accounts for swap...")
        swap_token_account = sell_get_token_account(solana_client, payer.pubkey(), mint)
        WSOL_token_account, WSOL_token_account_Instructions = get_token_account(solana_client, payer.pubkey(), sol)


        if swap_token_account == None:
            print("swap_token_account not found...")
            return False

        else:
            """Make swap instructions"""
            print("5. Create Swap Instructions...")
            instructions_swap = make_swap_instruction(amount_in,
                                                      swap_token_account,
                                                      WSOL_token_account,
                                                      pool_keys,
                                                      mint,
                                                      solana_client,
                                                      payer
                                                      )

            """Close wsol account"""
            print("6.  Create Instructions to Close WSOL account...")
            params = CloseAccountParams(account=WSOL_token_account, dest=payer.pubkey(), owner=payer.pubkey(),
                                        program_id=TOKEN_PROGRAM_ID)
            closeAcc = (close_account(params))

            """Create transaction and add instructions"""
            print("7. Create transaction and add instructions to Close WSOL account...")
            swap_tx = Transaction()
            signers = [payer]
            if WSOL_token_account_Instructions != None:
                swap_tx.add(WSOL_token_account_Instructions)
            swap_tx.add(instructions_swap)
            swap_tx.add(closeAcc)

            """Send transaction"""
            try:
                print("8. Execute Transaction...")
                start_time = time.time()
                txn = solana_client.send_transaction(swap_tx, *signers)

                """Confirm it has been sent"""
                txid_string_sig = txn.value
                print("9. Confirm it has been sent... ", txid_string_sig)
                checkTxn = True
                while checkTxn:
                    try:
                        status = solana_client.get_transaction(txid_string_sig, "json")
                        FeesUsed = (status.value.transaction.meta.fee) / 1000000000
                        if status.value.transaction.meta.err == None:
                            print("[create_account] Transaction Success", txn.value)
                            print(f"[create_account] Transaction Fees: {FeesUsed:.10f} SOL")

                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(f"Execution time: {execution_time} seconds")

                            if user_id is not None:
                                if not automatic:
                                    update, context = update_context[user_id]
                                    await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                                                   text="Transaction Success\n")
                                else:
                                    update, context = update_context[user_id]
                                    await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                                                   text="TP hit!\n")

                                    #update order with same order_seed
                                    orders = limit_orders.get(user_id, {})
                                    for key in list(orders.keys()):
                                        order = orders[key]
                                        if order.get('order_seed', "") == order_seed:
                                            order['txid'] = txid_string_sig
                                            order['status'] = "completed"
                                            break


                            txnBool = False
                            checkTxn = False
                            return txid_string_sig
                        else:

                            orders = limit_orders.get(user_id, {})
                            for key in list(orders.keys()):
                                order = orders[key]
                                if order.get('order_seed', "") == order_seed:
                                    order['status'] = "completed"
                                    break

                            print("Transaction Failed")
                            if user_id is not None:
                                try:
                                    update, context = update_context[user_id]
                                    await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                                                   text="Transaction Failed\n")
                                except:
                                    pass

                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(f"Execution time: {execution_time} seconds")




                            checkTxn = False
                            return False

                    except Exception as e:
                        print(f"{count}e|Sell ERROR {token_symbol}", f"[Raydium]: {e}")

                        print("Sleeping...", e)
                        await asyncio.sleep(1)
                        print("Retrying...")
                        count = count + 1
                        if count >= 70:
                            txnBool = False
                            checkTxn = False
                            return False

            except RPCException as e:
                print(amount_in,"ERR1", e)
                if automatic:
                    try:
                        orders = limit_orders.get(user_id, {})
                        for key in list(orders.keys()):
                            order = orders[key]
                            if order.get('order_seed', "") == order_seed:
                                st = order['status']
                                if st == "":
                                    st = "1"
                                else:
                                    st = str(int(st)+1)
                                order['status'] = st
                                break
                        #update, context = update_context[user_id]
                        #await context.bot.send_message(chat_id=update.effective_message.chat_id,
                        #                                text=f"Failed to TP\n`{token_address}`\n", parse_mode="Markdown")
                    except:
                        pass
                #print(f"e|SELL ERROR {token_symbol}", f"[Raydium]: {e.args[0].message}")
                txnBool = False
                return False

            except Exception as e:
                print(amount_in,"ERR2", e)
                try:
                    if automatic:
                        orders = limit_orders.get(user_id, {})
                        for key in list(orders.keys()):
                            order = orders[key]
                            st = order['status']
                            if st == "":
                                st = "1"
                            else:
                                st = str(int(st) + 1)
                            order['status'] = st
                        #update, context = update_context[user_id]
                        #await context.bot.send_message(chat_id=update.effective_message.chat_id,
                        #                                text=f"Failed to TP\n`{token_address}`\n", parse_mode="Markdown")
                except:
                    pass
                #print(f"Error: [{e}]...\nEnd...")
                #print(f"e|SELL Exception ERROR {token_symbol}", f"[Raydium]: {e.args[0].message}")
                txnBool = False
                return False

async def coming_soon(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Coming soon")


async def donate_sol(update, context):
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solana.rpc.api import Client
    from solders.system_program import TransferParams, transfer
    from solana.transaction import Transaction
    user_id = str(update.message.from_user.id)

    private_key = private_keys.get(user_id, "")
    if private_key == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                       text="You need to set your private key first")
        return

    sender = Keypair.from_seed(private_key)

    receiver = Pubkey.from_string("8kbahXTBSPzrUCwm7TmwPLUNNaLrUYTzoNfzsTWUv2T")

    one_sol = 1000000000
    transfer_fee = transfer(TransferParams(from_pubkey=sender.pubkey(), to_pubkey=receiver, lamports=one_sol//100))
    txn = Transaction().add(transfer_fee)
    try:
        solana_client = random.choice(clients)
        solana_client.send_transaction(txn, sender)
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Donation successful")
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Donation failed")

async def withdraw_sol(update: Update, context, solana_address):
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solana.rpc.api import Client
    from solders.system_program import TransferParams, transfer
    from solana.transaction import Transaction

    user_id = str(update.message.from_user.id)
    private_key = private_keys.get(user_id, "")
    if private_key == "":
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="You need to set your private key first")
        return

    sender = Keypair.from_seed(private_key)

    receiver = Pubkey.from_string(solana_address)

    full_total_receiver_balance = await get_sol_balance(update, context, sender.pubkey(), lamports=True)
    full_total_receiver_balance = full_total_receiver_balance - 2000000


    total_receiver_balance = int(full_total_receiver_balance * 0.99)
    fee = full_total_receiver_balance - total_receiver_balance
    fee_address = Pubkey.from_string("8kbahXTBSPzrUCwm7TmwPLUNNaLrUYTzoNfzsTWUv2T")
    transfer_fee = transfer(TransferParams(from_pubkey=sender.pubkey(), to_pubkey=fee_address, lamports=fee))

    transfer_ix = transfer(TransferParams(from_pubkey=sender.pubkey(), to_pubkey=receiver, lamports=total_receiver_balance))

    txn = Transaction().add(transfer_ix)
    txn.add(transfer_fee)
    try:
        solana_client = random.choice(clients)
        solana_client.send_transaction(txn, sender)
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Withdraw successful")
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_message.chat_id, text="Withdraw failed")

async def show_snipe_menu(update: Update, context):

    try:
        user_id = str(update.message.from_user.id)
    except:
        user_id = str(update.callback_query.from_user.id)
    private_key = private_keys.get(user_id, "")
    chat_id = update.effective_message.chat_id

    print("User id", user_id)

    if private_key == "":
        private_key = generate_private_key()
        private_keys[user_id] = private_key
        if pickle_enabled:
            pickle.dump(private_keys, open("KEYS.pkl", "wb"))


    public_key = Keypair.from_seed(private_key).pubkey()

    balance = await get_sol_balance(update, context, public_key)

    address = cas.get(user_id, "x")
    if address == "N/A":
        print("No address found")
        #url = f"[3TtnKvF1R99kpVYEANKz3TYG7HzQNnRqqbC4KscJMjYc](https://dexscreener.com/solana/3TtnKvF1R99kpVYEANKz3TYG7HzQNnRqqbC4KscJMjYc)"
        #cas[user_id] = "3TtnKvF1R99kpVYEANKz3TYG7HzQNnRqqbC4KscJMjYc"
        #address = "3TtnKvF1R99kpVYEANKz3TYG7HzQNnRqqbC4KscJMjYc"
    elif address == "x":
        url = f"Any"
        cas[user_id] = "x"
    else:
        url = f"[{address}](https://dexscreener.com/solana/{address})"
    amount = amounts.get(user_id, 0.01)

    amounts[user_id] = amount

    token_balance = await get_token_balance(token_address=address, wallet_address=str(public_key))

    print("Wallet address", str(public_key))
    print("Address", address)
    print("Token balance", token_balance)

    soltama_balance = await get_token_balance(token_address=soltama_address, wallet_address=str(public_key))

    print("Soltama balance", soltama_balance)

    min_liq = minumin_liqs.get(user_id, None)
    if min_liq == None:
        min_liq = 10
        minumin_liqs[user_id] = min_liq

    max_liq = maximum_liqs.get(user_id, None)
    if max_liq == None:
        max_liq = 100
        maximum_liqs[user_id] = max_liq


    entry_delay = entry_delays.get(user_id, None)
    if entry_delay == None:
        entry_delay = 0
        entry_delays[user_id] = entry_delay

    mint_2_liq_dealy = mint_2_liquidity_delays.get(user_id, None)
    if mint_2_liq_dealy == None:
        mint_2_liq_dealy = 0
        mint_2_liquidity_delays[user_id] = mint_2_liq_dealy

    try:
        symbol = await get_token_symbol_async(address)
    except:
        symbol = "CA Tokens"

    socials = require_socials.get(user_id, False)

    text = "🦈Sharkshooter🦈\n\n" \
            f"*🏠Address:* `{public_key}`\n[solscan](https://solscan.io/address/{public_key})\n\n" \
           f"*🦈SHARKS:* {round(soltama_balance,2)}\n" \
            f"*💰{symbol}:* {round(token_balance,2):,}\n" \
            f"*🏧SOL:* {round(balance,5)}\n\n" \
           f"*🔫SNIPER SETTING:*\n" \
           f"*📫Active CA:* {url}\n" \
           f"*🧮Amount:* {amount} SOL\n" \
           f"*👐Max liquidity:* {max_liq} SOL" \
           f"*🤏Min liquidity:* {min_liq} SOL\n" \
           f"*⏳️Entry delay:* {entry_delay} seconds\n" \
           f"*⏳️Mint2LP delay:* {mint_2_liq_dealy} seconds\n" \
           #f"🔗Require socials: {'👍' if socials else '👎'}\n\n" \
            #"*OPEN SNIPES:*\n" \
            #"➡ $SOLTAMA / 1 SOL\n" \
            #"➡ $ORYM / 0.2 SOL"

    #info = {
    #    "user_id": user_id,
    #    "amount": tokens_bought * snipe_limit["amount"],
    #    "uiAmount": uiAmount,
    #    "target_price": token_price * (1 + snipe_limit["profit"]),
    #    "token": await get_token_symbol_async(token_address),
    #    "stop_loss": False,
    #    "id": id + 1,
    #    "address": token_address,
    #}

    orders = limit_orders.get(user_id, {})
    if len(orders) > 0:
        text += "*OPEN LIMIT ORDERS:*\n"
    for order_key in list(orders.keys()):
        order = orders[order_key]
        status = order.get("status", "waiting")
        #text += f"*{'SL' if order['stop_loss'] else 'TP'} {order['token']}* / {order['amount']} @ {order['target_market_cap']}\n"
        text += f"*{order['id']}:* {'😥' if order['stop_loss'] else '🤩'} Sell *{order['uiAmount']:,} {order['token']}* @ {round(order['target_price'],6)}$ ({status})\n"
    if len(orders) > 0:
        text += "\n"

    #info = {
    #    "amount": amount,
    #    "profit": profit,
    #    "id": id + 1,
    #    "user_id": user_id,
    #}

    orders = snipe_limit_orders.get(user_id, [])
    if len(orders) > 0:
        text += "*AUTOMATIC TP's:*\n"
    for order in orders:
        # text += f"*{'SL' if order['stop_loss'] else 'TP'} {order['token']}* / {order['amount']} @ {order['target_market_cap']}\n"
        text += f"*{order['id']}:*🤖 Sell *{int(order['amount']*100)}%* if in profit by *{int(order['profit']*100)}%*\n"
    text += "\n"

    my_snipes = snipes.get(user_id, [])
    if len(my_snipes) > 0:
        text += "*MY SNIPES:*\n"
    for snipe in my_snipes:
        status = snipe['snipe_status'] #pending, fail, success, detected
        #switch case
        if status == "pending":
            status = "🦈"
        elif status == "fail":
            status = "😥"
        elif status == "success":
            status = "✅"
        elif status == "detected":
            status = "🕒"

        ml = snipe['min_liq']
        maxl = snipe['max_liq']

        tx = snipe.get("snipe_tx", None)
        tx_link = ""
        if tx != None:
            tx_link = f"([tx](https://solscan.io/tx/{tx}))"

        addr = snipe['token_address'][0:10] if snipe['token_address'] != "x" else "Any"
        text += f"*{snipe['id']}:* {status} *{float(snipe['amount']):,} SOL* loaded for *{addr}* {tx_link} (🤏{ml}, 👐{maxl})\n"

    await context.bot.send_message(chat_id=chat_id,
                                   text=text,
                                   reply_markup=get_sniper_menu(),
                                   parse_mode="markdown",
                                   disable_web_page_preview=True)

def generate_private_key():
    keypair = Keypair()
    priv = keypair.secret()
    return priv

def calculate_liquidity_addition(transaction):
    liquidity_additions = {}

    #return a dictionary of the difference in balances on the address stored in Raydium_Liquidity_Pool_V4
    #key is the token address, value is the difference in balance

    for item in transaction["result"]["meta"]["postTokenBalances"]:
        #print("XXX",item)
        if item['owner'] != Raydium_Authority_V4:
            continue
        token_address = item['mint']
        token_amount = item['uiTokenAmount']['uiAmount']
        if token_amount == "None":
            token_amount = 0
        liquidity_additions[token_address] = token_amount


    return liquidity_additions

def check_signature_task(client, signature):
    try:
        signature = signature['signature']
    except:
        pass
    sig = Signature.from_string(signature)


    # print("Signature:", signature)
    # print("SIG:", sig)
    count = 0

    event_loop = asyncio.new_event_loop()
    while True:
        try:
            transaction_json = client.get_transaction(sig, max_supported_transaction_version=0).to_json()
            transaction = json.loads(transaction_json)
            instuctions = transaction['result']['transaction']['message']['instructions']
            break
        except Exception as e:
            #print("\tasx", e)
            pass
        count += 1
        if count > 500:
            print("ERROR")
            return


    for instuction in instuctions:
        data = instuction['data']
        bytes_data = data.encode()

        program_index = instuction['programIdIndex']
        program_id = transaction['result']['transaction']['message']['accountKeys'][program_index]

        if program_id != Raydium_Liquidity_Pool_V4:
            continue
        if data == "A":
            continue

        if len(data) == 35:

            print("\n\nRaydium IDO detected")
            print(time.strftime("%H:%M:%S", time.localtime()))
            print("Signature:", signature)

            liq = calculate_liquidity_addition(transaction)
            print("Token amounts: ",liq)

            #print("Transaction:", transaction)

            sol_amount = liq.get(sol_address, 0)

            keys = set(liq.keys())
            keys_copy = copy.deepcopy(keys)

            try:
                keys_copy.remove(sol_address)
            except:
                return
            token_address = keys_copy.pop()

            token_amount = liq.get(token_address, 0)

            ratio = token_amount / sol_amount

            #snipes["876405598"] = [{'amount': 0.001, 'min_liq': 0.05, 'token_address': 'x', 'user_id': '876405598', 'id': 1, 'completed': False, 'timestamp': 1705141711}]
            snipes_copy = copy.deepcopy(snipes)

            solana_price = get_solana_price_sync()
            token_price = 1 / (ratio / solana_price)


            for user_id, user_snipes in snipes_copy.items():
                delay2 = mint_2_liquidity_delays.get(user_id, 0)
                delay = entry_delays.get(user_id, 0)
                for user_snipe in user_snipes:
                    #print("XXXXXX", user_snipe)
                    if (str(user_snipe['token_address']).lower() == str(token_address).lower() or user_snipe['token_address'] == "x") and user_snipe['snipe_status'] == "pending":
                        if user_snipe['min_liq'] <= sol_amount <= user_snipe['max_liq']:
                            print("Snipe detected!", user_id)
                            client = random.choice(clients)
                            pk = private_keys.get(user_id, None)
                            keypair = Keypair.from_seed(pk)

                            try:
                                snipes[user_id][user_snipe['id']-1]["snipe_status"] = "detected"
                            except:
                                continue

                            try:
                                event_loop.run_until_complete(buy(client, token_address, keypair,
                                                                  entry_delay=delay,
                                                                  mint_2_liq_delay=delay2,
                                                                  snipe=user_snipe,
                                                                  transaction=transaction,
                                                                  user_id=user_id,
                                                                  take_profit=True,
                                                                  sol_amount=sol_amount,
                                                                  token_price=token_price,
                                                                  min_liq=user_snipe['min_liq'],
                                                                  max_liq=user_snipe['max_liq']))
                            except Exception as e:
                                print(e)
                                pass

                            #token_marketcap = get_token_marketcap_sync(token_address)
                            #update, context = update_context[user_id]
                            #take_profit_task(context, update, user_id, amount, token_marketcap*2, token_address)
                            break









            #print("Transaction:", transaction,)



            #print(transaction)
            #exit(0)
    #print("\tNO ADDED LP")
    #exit(0)

def check_for_new_transactions(client, liquidity_pool_address, first=False):
    latest_slot = client.get_slot().value
    #print("Latest slot:", latest_slot)

    # Get the recent transaction signatures
    pubkey = Pubkey.from_string(liquidity_pool_address)
    signatures_json = client.get_signatures_for_address(pubkey, limit=1000).to_json()
    signatures = json.loads(signatures_json)
    # Filter for transactions calling the specified program


    count = 0
    #print("First", signatures['result'][-1]['slot'])
    #print("Last", signatures['result'][0]['slot'])

    filtered_signatures = []

    for signature in signatures['result'][::-1]:
        if signature['err'] != None or my_queue.includes(signature['signature']):
            continue

        count += 1

        # print("\n\t",signature)
        # continue

        my_queue.put(signature['signature'])

        filtered_signatures.append(signature)

        try:
            #print("\tRaydium_Liquidity_Pool_V4 tx", signature['signature'], "slot:", signature['slot'])
            unparsed_transactions.put(signature)
            # print(f"Created task {count}")
            pass
        except:
            pass
    #print("TX added to queue:", count)
    #print("Signatures:", (filtered_signatures))

    return


def limit_order_checker():
    event_loop = asyncio.new_event_loop()
    while True:
        for user_id in list(limit_orders.keys()):
            user_orders = limit_orders.get(user_id, {})
            for key in list(user_orders.keys()):
                order = user_orders[key]
                """
                    info = {
                        "user_id": user_id,
                        "amount": round(amount, 4),
                        "target_price": target_price,
                        "token": await get_token_symbol_async(token_address),
                        "stop_loss": stop_loss,
                        "id": id+1,
                        address: token_address,
                    }
                """

                try:
                    target_price = float(order["target_price"])
                    ca = order["address"]
                    amount = order["amount"]
                    stop_loss = order["stop_loss"]
                    token_address = order["address"]
                    status = order.get("status", "")

                    if status == "completed":
                        del user_orders[key]
                        continue

                    if status == "in progress":
                        continue

                    if len(status) == 1 and int(status) > 5:
                        continue

                    solana_client = random.choice(clients)
                    cached = prices_cache.get(token_address, None)
                    unix_time = int(time.time())

                    if cached is None:
                        # print("NO CACHE")
                        prices_cache[token_address] = {"price": get_token_price_sync(token_address),
                                                           "last_update": unix_time}

                    if unix_time - prices_cache[token_address]["last_update"] > 2:
                        # print("UPDATING CACHE")
                        prices_cache[token_address] = {"price": get_token_price_sync(token_address),
                                                           "last_update": unix_time}

                    cached = prices_cache[token_address]

                    actual_price = float(cached["price"])

                    # print("TP TASK", user_id, amount, target_market_cap, token_address, actual_market_cap)

                    condition = actual_price >= target_price if not stop_loss else actual_price <= target_price

                    if condition:
                        print("SELLING")
                        private_key = private_keys[user_id]
                        pubkey = Keypair.from_seed(private_key)
                        order["status"] = "in progress"
                        order["order_seed"] = random.randint(0, 10000000)
                        event_loop.run_until_complete(sell(solana_client, ca, pubkey, amount, user_id=user_id, automatic=True, token_address=token_address, order_seed=order["order_seed"]))
                except Exception as e:
                    print("tick exception ", e)
                    continue

        print("tick")
        time.sleep(2)

def parser():
    client_index = 0
    while True:
        if unparsed_transactions.qsize() == 0:
            #print("No transactions to parse")
            time.sleep(5)
            continue


        #check_signature_task(clients[client_index], signature)
        #asyncio.run(check_signature_task(clients[client_index], signature))



        signature = unparsed_transactions.get()
        t = Thread(target=check_signature_task, args=(clients[client_index], signature))
        t.start()

        client_index += 1
        if client_index == len(clients):
            client_index = 0
        #time.sleep(0.1)

    import timeit
    first = True
    client_index = 3


def reader():
    import timeit
    first = True
    client_index = 3
    while True:
        start = timeit.default_timer()
        try:
            check_for_new_transactions(clients[client_index], Raydium_Liquidity_Pool_V4, first=first)
        except:
            pass
        time.sleep(0.1)
        first = False
        stop = timeit.default_timer()
        print('Time: ', stop - start, "s\n")
        client_index += 1
        if client_index >= len(clients):
            client_index = 0
        print("Backlog:", unparsed_transactions.qsize())


if __name__ == "__main__":

    url1 = "https://solana-mainnet.g.alchemy.com/v2/KHy8Mbp-YVoAqH_UMldcUXyDDQ4RjGRz"
    url2 = "https://solana-mainnet.g.alchemy.com/v2/-jEcWdVynChRGF3cqIq11faDEukXpgJX"
    url3 = "https://solana-mainnet.g.alchemy.com/v2/x7UWQLtqem9ehlx8DEzeIa8yDvIq0Pch"
    url4 = "https://solana-mainnet.g.alchemy.com/v2/xqbrpOOMRjpcV0QNEVjX0FPuTGEbz-OH"
    url5 = "https://solana-mainnet.g.alchemy.com/v2/RpH_XI73kfXulOpw1unMCyt77I_TQJB0"
    url6 = "https://solana-mainnet.g.alchemy.com/v2/xDGza-JUb4g07NGRuGJRlfu7Tky5lqHD"
    url7 = "https://solana-mainnet.g.alchemy.com/v2/tEGZpuuYrtJ5d8d_BAdGt8qCvZtgVv_R"
    url8 = "https://solana-mainnet.g.alchemy.com/v2/OXFO61hihFtMqjpdYFpRrWaZkyh-Z9hI"


    urls = [url1, url2, url7, url3, url4, url5, url6, url8]

    client1 = Client(url1)
    client2 = Client(url2)
    client7 = Client(url7)
    client3 = Client(url3)
    client4 = Client(url4)
    client5 = Client(url5)
    client6 = Client(url6)
    client8 = Client(url8)
    clients = [client1, client2, client7, client4, client3, client5, client6, client8]

    try:
        if pickle_enabled:
            private_keys = pickle.load(open("KEYS.pkl", "rb"))
    except:
        pass


    try:
        if pickle_enabled:
            snipes = pickle.load(open("snipes.pkl", "rb"))
    except:
        pass

    try:
        if pickle_enabled:
            limit_orders = pickle.load(open("limit_orders.pkl", "rb"))
    except:
        pass

    try:
        if pickle_enabled:
            snipe_limit_orders = pickle.load(open("snipe_limits.pkl", "rb"))
    except:
        pass


    Raydium_Liquidity_Pool_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
    Raydium_Authority_V4 = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
    sol_address = "So11111111111111111111111111111111111111112"

    soltama_address = "EePJGdJHNn8DunCcQsLFBtGpkg9pPoZDV6JiVCVSTkib"#"3TtnKvF1R99kpVYEANKz3TYG7HzQNnRqqbC4KscJMjYc"

    metaplex_address = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
    token_program = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"


    cached_pool_keys = {}

    #print(get_metadata_from_IDO_signature("57rBa3eDr7Z4QoTKZM7nFxkKkAAARuAkbCdxoCwrcJtxhJkozj2vZJxgEM1nm9rH5Y29UCvDRy7L87eVe5QQGFLX"))

    #exit(0)

    #check_signature_task(client7, "bDfUdCoU6t6urkLeAbQHs7HK1ejRufkAUnmEhUZhugeuPuBj4stKW2zoENbpWL8EE8AgmTotvvhTgS6qmSowgjJ")

    #transacton = client7.get_transaction(Signature.from_string("4Gn6gXUXKwo5VoXY6cxC2yR1pVE66YozPHMkgBFH8mEDpbyzaKT2sWzoTtbfXsDjZGnaY1YUQnfYSSUedF8rsHvE"),max_supported_transaction_version=0)
    #print(get_pool_keys_from_transaction(json.loads(transacton.to_json())))
    #exit(0)

    #for order in limit_orders:
    #    print(order)
    #    print("----")


    #start = time.time()
    #print("start")
    #mint = Pubkey.from_string("6ibtxHd2nrJi6jtEZHcjyyrSPBimPXwsSFf835YByYf5")
    #print("keys", fetch_pool_keys(str(mint)))
    #end = time.time()
    #print("time", end - start)
    #exit(0)


    #using threading
    t = Thread(target=parser)
    t.start()
    t2 = Thread(target=reader)
    t2.start()
    t3 = Thread(target=limit_order_checker)
    t3.start()

    app = Application.builder().token(key)\
        .connection_pool_size(15000000)\
        .get_updates_connection_pool_size(15000000)\
        .pool_timeout(1500000)\
        .get_updates_pool_timeout(1500000)\
        .build()

    # Command to show the menu
    app.add_handler(CommandHandler("start", show_snipe_menu, block=False))
    app.add_handler(CallbackQueryHandler(button_callback, block=False))
    app.add_handler(MessageHandler(filters.ALL, handle_message, block=False))

    print("Bot started")
    app.run_polling()
