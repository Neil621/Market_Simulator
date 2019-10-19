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
    orders_df = pd.read_csv(orders_file, index_col='Date', parse_dates=True, na_values=['nan'])
    start_date = orders_df.index.min()
    end_date = orders_df.index.max()

    # Fetch stocks prices
    stocks = orders_df["Symbol"].unique().tolist()
    stocks_dict = {}
    for symbol in stocks:
        stocks_dict[symbol] = get_data([symbol], pd.date_range(start_date, end_date), colname='Adj Close')
        stocks_dict[symbol] = stocks_dict[symbol].resample("D").fillna(method="ffill")
        stocks_dict[symbol] = stocks_dict[symbol].fillna(method="bfill")

    # List the trading days
    SPY = get_data(['SPY'], pd.date_range(start_date, end_date))
    trading_days = pd.date_range(start_date, end_date, freq="D")
    not_trading_days = []
    for day in trading_days:
        if day not in SPY.index:
            not_trading_days.append(day)
    trading_days = trading_days.drop(not_trading_days)

    for day in orders_df.index:
        if day not in trading_days:
            raise Exception("One of the order day is missing in trading days")

    # Initialization of portfolio DataFrame
    portvals = pd.DataFrame(index=trading_days, columns=["portfolio_value"] + stocks)

    # Compute portfolio value for each trading day in the period
    current_value = start_val
    previous_day = None
    for today in trading_days:

        # Copy previous trading day's portfolio state
        if previous_day is not None:
            portvals.loc[today, :] = portvals.loc[previous_day, :]
            portvals.loc[today, "portfolio_value"] = 0
        else:
            portvals.loc[today, :] = 0

        # Execute orders
        if today in orders_df.index:
            today_orders = orders_df.loc[[today]]
            for _, order in today_orders.iterrows():
                symbol = order["Symbol"]
                operation = order["Order"]
                shares = order["Shares"]
                stock_price = stocks_dict[symbol].loc[today, symbol]

                if operation == "BUY":
                    stock_price = (1 + impact) * stock_price
                    current_value -= stock_price * shares
                    current_value -= commission
                    portvals.loc[today, symbol] += shares
                else:
                    stock_price = (1 - impact) * stock_price
                    current_value += stock_price * shares
                    current_value -= commission
                    portvals.loc[today, symbol] -= shares

        # Update portfolio value
        for symbol in stocks:
            stock_price = stocks_dict[symbol].loc[today, symbol]
            portvals.loc[today, "portfolio_value"] += portvals.loc[today, symbol] * stock_price
        portvals.loc[today, "portfolio_value"] += current_value

        previous_day = today

    # Remove empty lines
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
   # portvals = portvals[['IBM']]  # remove SPY  		   	  			  	 		  		  		    	 		 		   		 		  
   # rv = pd.DataFrame(index=portvals.index, data=portvals.values)  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
   # return rv  		   	  			  	 		  		  		    	 		 		   		 		  
   # return portvals  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
def test_code():  		   	  			  	 		  		  		    	 		 		   		 		  
    # this is a helper function you can use to test your code  		   	  			  	 		  		  		    	 		 		   		 		  
    # note that during autograding his function will not be called.  		   	  			  	 		  		  		    	 		 		   		 		  
    # Define input parameters  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
    of = "./orders/orders2.csv"  		   	  			  	 		  		  		    	 		 		   		 		  
    sv = 1000000  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
    # Process orders  		   	  			  	 		  		  		    	 		 		   		 		  
    portvals = compute_portvals(orders_file = of, start_val = sv)  		   	  			  	 		  		  		    	 		 		   		 		  
    if isinstance(portvals, pd.DataFrame):  		   	  			  	 		  		  		    	 		 		   		 		  
        portvals = portvals[portvals.columns[0]] # just get the first column  		   	  			  	 		  		  		    	 		 		   		 		  
    else:  		   	  			  	 		  		  		    	 		 		   		 		  
        "warning, code did not return a DataFrame"  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
    # Get portfolio stats  		   	  			  	 		  		  		    	 		 		   		 		  
    # Here we just fake the data. you should use your code from previous assignments.  		   	  			  	 		  		  		    	 		 		   		 		  
    start_date = dt.datetime(2008,1,1)  		   	  			  	 		  		  		    	 		 		   		 		  
    end_date = dt.datetime(2008,6,1)  		   	  			  	 		  		  		    	 		 		   		 		  
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]  		   	  			  	 		  		  		    	 		 		   		 		  
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
    # Compare portfolio against $SPX  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Date Range: {start_date} to {end_date}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Sharpe Ratio of Fund: {sharpe_ratio}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Sharpe Ratio of SPY : {sharpe_ratio_SPY}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Cumulative Return of Fund: {cum_ret}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Cumulative Return of SPY : {cum_ret_SPY}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Standard Deviation of Fund: {std_daily_ret}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Standard Deviation of SPY : {std_daily_ret_SPY}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Average Daily Return of Fund: {avg_daily_ret}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Average Daily Return of SPY : {avg_daily_ret_SPY}")  		   	  			  	 		  		  		    	 		 		   		 		  
    print()  		   	  			  	 		  		  		    	 		 		   		 		  
    print(f"Final Portfolio Value: {portvals[-1]}")  		   	  			  	 		  		  		    	 		 		   		 		  
  		   	  			  	 		  		  		    	 		 		   		 		  
if __name__ == "__main__":  		   	  			  	 		  		  		    	 		 		   		 		  
    test_code()  		   	  			  	 		  		  		    	 		 		   		 		  
