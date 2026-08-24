The Project Crypto potfolio tracker:(PLAN):

How it look:
A clean UI 
with a option of portfolio to add the coins to keep the track of them 

Questions:

What information should be stored for one cryptocurrency?
=The Name and symbol of the currency


How will the user interact with the program?
=User opens the program directly see there portfolio 
they can add the coins and remove the coins 
then save the portfolio
then exit

What happens in these situations?

The portfolio is empty?
= there will be a message in the center saying the portfolio is empty add coins. 

The user tries to remove a coin that doesn't exist?
the remove option ailable on the con like when the coin add there will be a small x button to remove so user can't remove the coin without adding it in portfolio.

The user adds the same coin twice?
The repetative values are ignore (So no output will be generate and a message appers that sayes already existed.).

The program is opened for the first time and no saved portfolio exists?
There will be default portfolio exist always so people could start with that

Explain to me why you chose a dictionary for storing your coin symbols?
= Because the dictionary are mutable and don't allow repetative values

File exists but JSON is damaged?
So if the JSON is damaged that we use json.JSONDecodeError and create a make the portfolio empty and give a warnning too after the empty portfolio be saved the previous json file will be fully overwrite and the json will be fix for the next time

What should the function be called?
for the easy understanding the function should be called save()

What information does the function need?
The function need tthe portfolio either its a empty or parsed from saved portfolio before 

Does the function need to return anything?
Since the function save the portfolio in json and write the data in the file so it did't need anything to return as of now as main() take its data from the json saved portfolio

Where should the success message go?
the saved funtion prints the saved

What should the parameter represent?
The parameter should be your_portfolio

What should the load function be called?
The load function should called data_back()

Does it need any parameter?
No it did,t need parameter

What should it return?
it should return the portfolio in set form

Should the error-handling messages live inside the load function or in main()?
it should live inside the load function as these error handling happend before the main menu

Design Decisions:

DD1:
Coin Symbols : BTC

DD2:
Invalid Coins : Since this is V1 and we are working on the coin add and remove so its not important so if someone add the invlid coin for not we will add this will improve this in future when we work on price aleart and price tracking

DD3:
Portfolio Name: For V1 we can create one portfolio which is by default portfolio and change the name.But will make multiple in future.


Learning while creating the project

JSON
