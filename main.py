import json
import requests
import sys
from pathlib import Path

BACKEND_URL = (f"https://fou-backend.onrender.com")

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

SAVE_FILE = BASE_DIR / "save_portfolio.json"

def get_coin_list():
    URL1 = (f"{BACKEND_URL}/coins")

    try:
        response_list = requests.get(URL1, timeout = 60)
    
    except requests.exceptions.Timeout:
        print("FOU server took too long to respond.")
        return None
    
    except requests.exceptions.RequestException:
        print("Could not connect to the FOU server")
        return None

    if response_list.status_code != 200:
        print("FOU server returned an error.")
        return None

    try:
        coin_list = response_list.json()
    
    except requests.exceptions.JSONDecodeError:
        print("FOU server returned invalid data.")
        return None

    if not isinstance(coin_list , list):
        print(response_list.status_code)
        print("Please try again later")
        return None
    else:
        return coin_list


def get_market_data(ids):
    join_ids = ",".join(ids)

    params2 = {
        "ids" : join_ids
                 }

    URL2 = (f"{BACKEND_URL}/market")

    try:
        request_data = requests.get(URL2, params= params2, timeout= 10)

    except requests.exceptions.Timeout:
        print("FOU server took too long to respond.")
        return None
    
    except requests.exceptions.RequestException:
        print("Could not connect to the FOU server")
        return None

    if request_data.status_code != 200:
        print("FOU server returned an error.")
        return None

    try:
        market_data = request_data.json()
    
    except requests.exceptions.JSONDecodeError:
        print("FOU server returned invalid data.")
        return None

    if not isinstance(market_data, list):
        return None
    else:
        return market_data

def find_coin(symbol, market_data):
    symbol = symbol.lower().strip()

    best_coin = None
    best_rank = None 
    fallback = None

    for coin in market_data:
        if coin["symbol"] != symbol:
            continue

        if fallback is None:
            fallback = coin

        rank = coin["market_cap_rank"]


        if rank is None:
            continue

        if best_rank is None:
            best_rank = rank
            best_coin = coin
        
        elif rank < best_rank :
            best_rank = rank
            best_coin = coin
    if best_coin is None :
        return fallback
    else:
        return best_coin


def load_portfolio():
    try:
        with open(SAVE_FILE, "r") as file:
            portfolio = json.load(file)

    except FileNotFoundError:
        portfolio = {}
    except (json.JSONDecodeError, TypeError):
        portfolio = {}
        print("Something went wrong with the saved file.\nA new portfolio was created.")

    return portfolio


def save_portfolio(portfolio):
    with open(SAVE_FILE, "w") as f:
        json.dump(portfolio, f)

    print("Your portfolio was saved.")


def add_coin(portfolio, coin_list):
    pending = []

    print("When done adding coins enter 'Done'.")
    while True:
        symbol = input("Enter the coin symbol (e.g., BTC): ").strip().upper()

        if symbol == "":
            continue

        if symbol == "DONE" :

                if not pending:
                    print("Please add something.")
                    break
                else:
                    batch_id = []
                    for symbol in pending:
                        for coin in coin_list:
                            if coin["symbol"] == symbol.lower():
                                batch_id.append(coin["id"])

                    market_data = get_market_data(batch_id)
                    
                    if market_data is None:
                        print("Please try again.")
                        return
                    
                    for symbol in pending:
                        result = find_coin(symbol, market_data)
                    
                        if not result:
                            print("Couldn't find the coin add another coin")
                            continue

                        else:
                            portfolio[symbol] = result["id"]

                            print(f"{symbol} is added to the portfolio.")      
                              
                    break


        if symbol in portfolio:
            print(f"{symbol} is already in the portfolio.")
        
        else:
            found = False
            for coin in coin_list:
                if coin["symbol"] == symbol.lower():
                    found = True
                    break
            
            if symbol in pending:
                print(f"{symbol} is already in added.")
            
            elif found:
                pending.append(symbol)
            
            elif found == False:
                print("Coin not found.")


def remove_coin(portfolio):
    if not portfolio:
            print("Your portfolio is empty. There is nothing to remove.")
            return
    
    print("Type 'Done' when finished.")
    
    while True:

        if not portfolio:
            print("Your portfolio is now empty.")
            break

        remove_symbol = input("Enter the coin symbol to remove: ").strip().upper()

        if remove_symbol == "DONE":
            print("Done removing coins.")
            break
        if remove_symbol == "":
            continue
        if remove_symbol not in portfolio:
            print(f"{remove_symbol} is not in the portfolio.")
        else:
            del portfolio[remove_symbol]
            print(f"{remove_symbol} was removed from the portfolio.")


def rank_key(coin):
    rank = coin["market_cap_rank"]
    if rank is None :
        rank = float("inf")
        
    return rank


def view_portfolio(portfolio):
    if not portfolio:
        print("Your portfolio is empty. Add a coin to get started.")
    else:
        all_ids = list(portfolio.values())
        
        result_view = get_market_data(all_ids)

        if result_view is None:
            print("Please try again.")
            return
        
        sort_data = sorted(result_view, key = rank_key)

        coin_width = 8

        visible_coin = []
        hidden_coin = 0

        for coin in sort_data:
            if coin["current_price"] == 0:
                hidden_coin += 1
            else:
                visible_coin.append(coin)
         
        for coin in visible_coin:
            if len(coin["symbol"]) > coin_width :
                coin_width = len(coin["symbol"])
            else:
                continue

        display_rows = []

        for number, coin in enumerate(visible_coin, start= 1):
            price = coin["current_price"]
            note = ""
            multiplier = 1
        
            while price <= 0.00000001: 
                price = price*1000
                multiplier *= 1000
            
            if multiplier == 1:
                note = ""
            elif multiplier == 1000:
                note = "/ 1K"
            elif multiplier == 1000000:
                note = "/ 1M"
            elif multiplier == 1000000000:
                note = "/ 1B"

            if price >= 1:
                formatted_price = f"${price:,.2f}"
            elif price >= 0.01:
                formatted_price = f"${price:,.4f}"
            else:
                formatted_price = f"${price:,.8f}"

            display_rows.append((number,coin["symbol"],formatted_price,note))

        price_width = len("PRICE")

        for row in display_rows:
            if price_width < len(row[2]):
                price_width = len(row[2])
            else:
                continue 
        
        base_table_width = 4+1+(coin_width)+3+(price_width)
        table_width = base_table_width

        for row in display_rows:
            if row[3] == "":
                continue
            else:
                Note_row_width = base_table_width +1 + len(row[3])

                if table_width < Note_row_width:
                    table_width = Note_row_width
                else:
                    continue
        
        header = f"{"#":<4} {"COIN":<{coin_width}} | {"PRICE":<{price_width}}"

        pipe_position = header.index("|")


        title = " PORTFOLIO "

        title_anchor = title.index("F")
        
        left_dashes = pipe_position - title_anchor

        right_dash = table_width - left_dashes - len(title)

        print(f"{"-"*left_dashes}{title}{"-"*right_dash}")

        print(header)

        print("-"*table_width)

        for row in display_rows:
            normal_row = (f"{f"{row[0]}.":<4} {row[1].upper():<{coin_width}} | {row[2]:<{price_width}}")

            if row[3] == "":
                print(normal_row)
            else:
                print(normal_row + " " + row[3]) 
        
        if hidden_coin == 0:
            return

        if hidden_coin == 1:
            print(f"{hidden_coin} coin hidden because its current price is zero.")
        
        else:
            print(f"{hidden_coin} coins hidden because their current price is zero.")
        
            


def main():
    portfolio = load_portfolio()

    coin_list = get_coin_list()

    choice = ""

    if coin_list is None:
        return
    

    while choice != "5":
        print("\n---- Options ----")
        print("1. Add Coin")
        print("2. View Portfolio")
        print("3. Remove Coin")
        print("4. Save Portfolio")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_coin(portfolio, coin_list)

        elif choice == "2":
            view_portfolio(portfolio)

        elif choice == "3":
            remove_coin(portfolio)

        elif choice == "4":
            save_portfolio(portfolio)


if __name__ == "__main__":
    main()
