import json


def load_portfolio():
    try:
        with open("save_portfolio.json", "r") as file:
            listed_portfolio = json.load(file)

        portfolio = set(listed_portfolio)
    except FileNotFoundError:
        portfolio = set()
    except (json.JSONDecodeError, TypeError):
        portfolio = set()
        print("Something went wrong with the saved file.\nA new portfolio was created.")

    return portfolio


def save_portfolio(portfolio):
    listed_portfolio = list(portfolio)

    with open("save_portfolio.json", "w") as f:
        json.dump(listed_portfolio, f)

    print("Your portfolio was saved.")


def main():
    portfolio = load_portfolio()
    choice = ""

    while choice != "5":
        print("\n---- Portfolio ----")
        print("1. Add Coin")
        print("2. View Portfolio")
        print("3. Remove Coin")
        print("4. Save Portfolio")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            symbol = input("Enter the coin symbol (e.g., BTC): ").strip().upper()
            if symbol == "":
                continue

            if symbol in portfolio:
                print(f"{symbol} is already in the portfolio.")
            else:
                portfolio.add(symbol)
                print(f"{symbol} was added to the portfolio.")

        elif choice == "2":
            if not portfolio:
                print("Your portfolio is empty. Add a coin to get started.")
            else:
                print("---- Your Portfolio ----")
                for item in portfolio:
                    print(item)

        elif choice == "3":
            if not portfolio:
                print("Your portfolio is empty. There is nothing to remove.")
                continue

            remove_symbol = input("Enter the coin symbol to remove: ").strip().upper()

            if remove_symbol == "":
                continue

            if remove_symbol not in portfolio:
                print(f"{remove_symbol} is not in the portfolio.")
            else:
                portfolio.remove(remove_symbol)
                print(f"{remove_symbol} was removed from the portfolio.")

        elif choice == "4":
            save_portfolio(portfolio)


main()
