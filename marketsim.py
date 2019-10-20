"""MC2-P1: Market simulator.  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
Copyright 2018, Georgia Institute of Technology (Georgia Tech)  		   	  			  	 		  		  		    	 		 		   		 		  
Atlanta, Georgia 30332  		   	  			  	 		  		  		    	 		 		   		 		  
All Rights Reserved  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
Template code for CS 4646/7646  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
Georgia Tech asserts copyright ownership of this template and all derivative  		   	  			  	 		  		  		    	 		 		   		 		  
works, including solutions to the projects assigned in this course. Students  		   	  			  	 		  		  		    	 		 		   		 		  
and other users of this template code are advised not to share it with others  		   	  			  	 		  		  		    	 		 		   		 		  
or to make it available on publicly viewable websites including repositories  		   	  			  	 		  		  		    	 		 		   		 		  
such as github and gitlab.  This copyright statement should not be removed  		   	  			  	 		  		  		    	 		 		   		 		  
or edited.  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
We do grant permission to share solutions privately with non-students such  		   	  			  	 		  		  		    	 		 		   		 		  
as potential employers. However, sharing with other current or future  		   	  			  	 		  		  		    	 		 		   		 		  
students of CS 7646 is prohibited and subject to being investigated as a  		   	  			  	 		  		  		    	 		 		   		 		  
GT honor code violation.  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
-----do not edit anything above this line---  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
Student Name: Neil Watt (replace with your name)  		   	  			  	 		  		  		    	 		 		   		 		  
GT User ID: nwatt3 (replace with your User ID)  		   	  			  	 		  		  		    	 		 		   		 		  
GT ID: 903476861  (replace with your GT ID)  		   	  			  	 		  		  		    	 		 		   		 		  
"""  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
import pandas as pd  		   	  			  	 		  		  		    	 		 		   		 		  
import numpy as np  		   	  			  	 		  		  		    	 		 		   		 		  
import datetime as dt  		   	  			  	 		  		  		    	 		 		   		 		  
import os 


from util import get_data, plot_data  		   	  			  	 		  		  		    	 		 		   		 		  


#def compute_portvals(orders_file = "./orders/orders.csv", start_val = 1000000, commission = 9.95, impact = 0.005):
    # TODO: Your code here
   # return portvals
def author():
        return 'nwatt3' 

    
    
def sharpe_ratio(portfolio_value, n=np.sqrt(252)):
    return n * average_daily_returns(portfolio_value) / standard_dev_daily_returns(portfolio_value)
    


def average_daily_returns(portfolio_value):
    daily_return = (portfolio_value / portfolio_value.shift(1)) - 1
    return daily_return[1:].mean()



def standard_dev_daily_returns(portfolio_value):
    daily_ret = (portfolio_value / portfolio_value.shift(1)) - 1
    return daily_ret[1:].std()

def cumul_ret(portfolio_value):
    cumul_ret = (portfolio_value /portfolio_value[0]) - 1
    return cumul_ret[-1]






def compute_portvals(orders_file="./orders/orders.csv", start_val=1000000, commission=9.95, impact=0.005):
    
    
    order_pdataframe = pd.read_csv(orders_file, index_col='Date', parse_dates=True, na_values=['nan'])
    start_date = order_pdataframe.index.min()
    end_date = order_pdataframe.index.max()

    
    
    # extract stock prices according to symbol
    stocks = order_pdataframe["Symbol"].unique().tolist()
    stock_dictionary = {}
    for symbol in stocks:
        stock_dictionary[symbol] = get_data([symbol], pd.date_range(start_date, end_date), colname='Adj Close')
        stock_dictionary[symbol] = stock_dictionary[symbol].resample("D").fillna(method="ffill")
        stock_dictionary[symbol] = stock_dictionary[symbol].fillna(method="bfill")

    #  extract trading days between the start and end dates
    

    
    SPX = get_data(['$SPX'], pd.date_range(start_date, end_date))
    market_trading_day = pd.date_range(start_date, end_date, freq="D")
    not_market_trading_day = []
    for day in market_trading_day:
        if day not in SPX.index:
            not_market_trading_day.append(day)
    market_trading_day = market_trading_day.drop(not_market_trading_day)

   
    
    
    portvals = pd.DataFrame(index=market_trading_day, columns=["portfolio_value"] + stocks)

   
    ## calc portval for every day in the date range from start to end date
    
    
    current_value = start_val
    previous_day = None
    for current_trading_day in market_trading_day:

        
        if previous_day is not None:
            portvals.loc[current_trading_day, :] = portvals.loc[previous_day, :]
            portvals.loc[current_trading_day, "portfolio_value"] = 0
        else:
            portvals.loc[current_trading_day, :] = 0

        #  carry out orders to buy etc
        if current_trading_day in order_pdataframe.index:
            current_trading_day_orders = order_pdataframe.loc[[current_trading_day]]
            for _, order in current_trading_day_orders.iterrows():
                symbol = order["Symbol"]
                operation = order["Order"]
                shares = order["Shares"]
                stock_price = stock_dictionary[symbol].loc[current_trading_day, symbol]

                if operation == "BUY":
                    stock_price = (1 + impact) * stock_price
                    current_value -= stock_price * shares
                    current_value -= commission
                    portvals.loc[current_trading_day, symbol] += shares
                else:
                    stock_price = (1 - impact) * stock_price
                    current_value += stock_price * shares
                    current_value -= commission
                    portvals.loc[current_trading_day, symbol] -= shares

        #  update portvals according to today's 
        for symbol in stocks:
            stock_price = stock_dictionary[symbol].loc[current_trading_day, symbol]
            portvals.loc[current_trading_day, "portfolio_value"] += portvals.loc[current_trading_day, symbol] * stock_price
        portvals.loc[current_trading_day, "portfolio_value"] += current_value

        previous_day = current_trading_day

    # get rid of spaces
    portvals = portvals.sort_index(ascending=True)
    return portvals.iloc[:,0].to_frame()


#def compute_portvals(orders_file = "./orders/orders.csv", start_val = 1000000, commission=9.95, impact=0.005):  		   	  			  	 		  		  		    	 		 		   		 		  
    # this is the function the autograder will call to test your code  		   	  			  	 		  		  		    	 		 		   		 		  
    # NOTE: orders_file may be a string, or it may be a file object. Your  		   	  			  	 		  		  		    	 		 		   		 		  
    # code should work correctly with either input  		   	  			  	 		  		  		    	 		 		   		 		  
    # TODO: Your code here  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
    # In the template, instead of computing the value of the portfolio, we just  		   	  			  	 		  		  		    	 		 		   		 		  
    # read in the value of IBM over 6 months  		   	  			  	 		  		  		    	 		 		   		 		  
   # start_date = dt.datetime(2008,1,1)  		   	  			  	 		  		  		    	 		 		   		 		  
   # end_date = dt.datetime(2008,6,1)  		   	  			  	 		  		  		    	 		 		   		 		  
    #portvals = get_data(['IBM'], pd.date_range(start_date, end_date))  		   	  			  	 		  		  		    	 		 		   		 		  
   # portvals = portvals[['IBM']]  # remove SPX  		   	  			  	 		  		  		    	 		 		   		 		  
   # rv = pd.DataFrame(index=portvals.index, data=portvals.values)  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
   # return rv  		   	  			  	 		  		  		    	 		 		   		 		  
   # return portvals  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
def test_code():  		   	  			  	 		  		  		    	 		 		   		 		  
    of = "./additional_orders/orders.csv"
    #of = "./orders/orders-short-bis.csv"
    #of = "./orders/orders.csv"
    #of = "./orders/orders2.csv"
    sv = 1000000

    # Process orders 			  		 			     			  	   		   	  			  	
    portvals = compute_portvals(orders_file = of, start_val = sv)
    #print(portvals)
    if isinstance(portvals, pd.DataFrame): 			  		 			     			  	   		   	  			  	
        portvals = portvals[portvals.columns[0]] # just get the first column
    else: 			  		 			     			  	   		   	  			  	
        "warning, code did not return a DataFrame" 			  		 			     			  	   		   	  			  	

    # Get portfolio stats
    start_date = portvals.index.min()
    end_date = portvals.index.max()
    SPX = get_data(['$SPX'], pd.date_range(start_date, end_date))
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio_ = [
        cumul_ret(portvals/portvals[0]),
        average_daily_returns(portvals/portvals[0]),
        standard_dev_daily_returns(portvals/portvals[0]),
        sharpe_ratio(portvals/portvals[0])
    ]
    cum_ret_SPX, avg_daily_ret_SPX, std_daily_ret_SPX, sharpe_ratio_SPX = [
        cumul_ret(SPX.iloc[:,1]/SPX.iloc[0,1]),
        average_daily_returns(SPX.iloc[:,1]/SPX.iloc[0,1]),
        standard_dev_daily_returns(SPX.iloc[:,1]/SPX.iloc[0,1]),
        sharpe_ratio(SPX.iloc[:,1]/SPX.iloc[0,1])
    ] 		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Date Range: {start_date} to {end_date}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Sharpe Ratio of Fund: {sharpe_ratio}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Sharpe Ratio of SPX : {sharpe_ratio_SPX}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Cumulative Return of Fund: {cum_ret}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Cumulative Return of SPX : {cum_ret_SPX}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Standard Deviation of Fund: {std_daily_ret}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Standard Deviation of SPX : {std_daily_ret_SPX}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Average Daily Return of Fund: {avg_daily_ret}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Average Daily Return of SPX : {avg_daily_ret_SPX}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Final Portfolio Value: {portvals[-1]}")  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
if __name__ == "__main__":  		   	  			  	 		  		  		    	 		 		   		 		  
    test_code()  		   	  			  	 		  		  		    	 		 		   		 		  
