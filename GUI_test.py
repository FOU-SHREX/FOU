import customtkinter as ctk

app = ctk.CTk()

tested_coin = []

header_frame = ctk.CTkFrame(app)
header_frame.grid(row= 0, column= 0, columnspan= 2, padx= 20, pady=20)

app.title("GUI TEST IS RUNNING")

app.geometry("500x500+450+200")

title = ctk.CTkLabel(
    header_frame,
    text= "FOU // CRYPTO WATCHLIST"
)

title.grid(row =0, column = 0, padx= 20, pady= 10)

input_frame = ctk.CTkFrame(app)
input_frame.grid(row= 1, column= 0, columnspan= 2, padx= 20, pady= 10)


coin_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text= "Enter the coin symbol... "
)
coin_entry.grid(row= 0, column= 0, padx= 20, pady= 10)

status_frame = ctk.CTkFrame(app)
status_frame.grid(row= 3, column= 0, columnspan= 2, padx= 20, pady= 10)

status = ctk.CTkLabel(
    status_frame,
    text= "STATUS // WAITING"
)
status.grid(row= 0, column= 0,columnspan= 2, padx= 20, pady= 5)

watchlist_frame= ctk.CTkFrame(app)
watchlist_frame.grid(row= 2, column= 0, columnspan= 2, padx= 20, pady= 10)

watchlist_title = ctk.CTkLabel(
    watchlist_frame,
    text= "WATCHLIST"
)
watchlist_title.grid(row= 0, column= 0, columnspan= 2, padx= 20, pady= 10)

rows_frame = ctk.CTkFrame(watchlist_frame)
rows_frame.grid(row= 1, column= 0, padx= 20, pady= 10)

def refresh_watchlist():
    for widget in rows_frame.winfo_children():
        widget.destroy()

    for number, coin in enumerate(tested_coin, start= 1):
        coin_label = ctk.CTkLabel(
            rows_frame,
            text= f"{number:02} // {coin}"
        )
        coin_label.grid(row= number -1, column= 0, padx= 20, pady= 5)

        remove_button= ctk.CTkButton(
            rows_frame,
            text= "x",
            width= 30,
            command= lambda c=coin: remove_coin(c)
        )
        remove_button.grid(row= number -1, column= 1)
    

def add_coin(event= None):
    symbol= coin_entry.get().upper().strip()
    if not symbol:
        status.configure(text= "STATUS // ENTER THE SYMBOL PLEASE")
        return
    if symbol in tested_coin:
        status.configure(text= f"STATUS // {symbol} IS ALREADY IN WATCHLIST")
        return
    tested_coin.append(symbol)

    refresh_watchlist()
    
    status.configure(text= f"STATUS // {symbol} RECEIVED")
    
    coin_entry.delete(0, "end")


def remove_coin(symbol):
    tested_coin.remove(symbol)
    refresh_watchlist()
    status.configure(text= f"STATUS // {symbol} REMOVED")
coin_entry.bind("<Return>", add_coin)

button = ctk.CTkButton(
    input_frame,
    text= "ADD",
    command= add_coin
)
button.grid(row= 0, column= 1, padx= 10, pady= 10)


app.mainloop()