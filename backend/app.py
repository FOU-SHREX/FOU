import os
import requests
import time
from fastapi import FastAPI, HTTPException, Request

coin_cache = None
coin_cache_time = 0
coin_cache_TTL = 6*60*60
market_cache = {}
market_cache_TTL = 30
rate_limit_store = {}
RATE_LIMIT = 60
RATE_WINDOW = 60

api_key = os.getenv("COINGECKO_API_KEY")

request_headers = {
    "x-cg-demo-api-key": api_key
}

app = FastAPI()

def check_rate_limit(request: Request):

    client_ip = request.client.host

    current_time = time.time()

    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = {
            "count": 1,
            "start_time": current_time
        }
    else:
        client_data = rate_limit_store[client_ip]

        elapse_time = current_time - client_data["start_time"]

        if elapse_time >= RATE_WINDOW:
            client_data["count"] = 1
            client_data["start_time"] = current_time

        else:
            client_data["count"] += 1

        if client_data["count"] > RATE_LIMIT:
            raise HTTPException(
                status_code= 429,
                detail= "Too many requests. Please try again later."
            )

@app.get("/")
def home():
    return("message: FOU Backend is running")

@app.get("/coins")
def get_coin(request: Request):

    check_rate_limit(request)

    global coin_cache, coin_cache_time

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Backend API key is not configured."
        )

    current_time = time.time()

    if coin_cache is not None and current_time - coin_cache_time < coin_cache_TTL:
        return coin_cache

    URL1 = (f"https://api.coingecko.com/api/v3/coins/list")

    try:
        response = requests.get(URL1, headers= request_headers, timeout= 10 )

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code= 504,
            detail="CoinGecko request timed out."
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code= 502,
            detail= "Could not connect to CoinGecko."
        )

    if response.status_code == 401 or response.status_code == 403:
        raise HTTPException(
            status_code= 502,
            detail= "CoinGecko authentication failed."
        )

    elif response.status_code == 429:
        raise HTTPException(
            status_code= 503,
            detail= "CoinGecko rate limit reached."
        )

    elif 500 <= response.status_code < 600:
        raise HTTPException(
            status_code= 502,
            detail= "CoinGecko server error."
        )

    elif response.status_code != 200:
        raise HTTPException(
            status_code= 502,
            detail="Could not get coin data from CoinGecko."
        )

    try:
        coin_list = response.json()

    except requests.exceptions.JSONDecodeError:
        raise HTTPException(
            status_code= 502,
            detail= "CoinGecko returned invalid data."
        )

    if not isinstance(coin_list, list):
        raise HTTPException(
            status_code = 502,
            detail="Could not get coin data from CoinGecko."
        )
    else:
        coin_cache = coin_list
        coin_cache_time = current_time
        return coin_cache

@app.get("/market")
def get_market(request: Request, ids: str):
    check_rate_limit(request)
    if not api_key:
        raise HTTPException(
            status_code = 500,
            detail= "Backend API key is not configured"
        )

    ids = ids.strip()

    if not ids:
        raise HTTPException(
            status_code= 400,
            detail= "Coin IDs are required."
        )

    id_list = ids.split(",")
    clean_ids = []

    for id in id_list:
        id = id.strip()

        if id == "":
            continue

        elif id in clean_ids:
            continue

        else:
            clean_ids.append(id)

    if not clean_ids:
        raise HTTPException(
            status_code= 400,
            detail= "Coin IDs are required."
        )

    if len(clean_ids) > 50:
        raise HTTPException(
            status_code= 400,
            detail= "Too many coin IDs. Maximum is 50."
        )

    cache_key = sorted(clean_ids)

    cache_key = ",".join(cache_key)

    ids = ",".join(clean_ids)

    current_time = time.time()

    if cache_key in market_cache:
        cache_entry = market_cache[cache_key]
        saved_time = cache_entry["time"]

        if current_time - saved_time < market_cache_TTL:
            return cache_entry["data"]
        else:
            del market_cache[cache_key]

    URL2 = (f"https://api.coingecko.com/api/v3/coins/markets")

    param1 = {
        "vs_currency": "usd",
        "ids": ids
    }

    try:
        response2 = requests.get(URL2, params= param1, headers= request_headers, timeout = 10)

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code= 504,
            detail= "CoinGecko request timed out."
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code= 502,
            detail= "Could not connect to CoinGecko."
        )

    if response2.status_code == 401 or response2.status_code == 403:
        raise HTTPException(
            status_code= 502,
            detail= "CoinGecko authentication failed."
        )

    elif response2.status_code == 429:
        raise HTTPException(
            status_code= 503,
            detail= "CoinGecko rate limit reached."
        )

    elif 500 <= response2.status_code < 600:
        raise HTTPException(
            status_code= 502,
            detail= "CoinGecko server error."
        )

    elif response2.status_code != 200:
        raise HTTPException(
            status_code= 502,
            detail= "Could not get market data from CoinGecko."
        )

    try:
        market_data = response2.json()

    except requests.exceptions.JSONDecodeError:
        raise HTTPException(
            status_code= 502,
            detail= "CoinGecko returned invalid data."
        )

    if not isinstance(market_data, list):
        raise HTTPException(
            status_code = 502,
            detail = "Could not get market data from CoinGecko."
        )

    else:
        market_cache[cache_key] = {
            "data": market_data,
            "time": time.time()
            }
        return market_data