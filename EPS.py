import os
import pandas as pd
import matplotlib.pyplot as plt


def symbol_to_path(symbol, base_dir="data"):
    """Return CSV file path given a ticker symbol"""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))

def get_data(symbol, dates):
    """Read stock data(adjusted close) for given symbols from CSV files"""
    df = pd.DataFrame(index=dates)

    tickers = ['M7EU']
    tickers.insert(1, symbol)

    for ticker in tickers:
        df_temp = pd.read_csv(symbol_to_path(ticker),index_col='Dates',
                              parse_dates=True, na_values = ['nan'])
        # Rename to prevent clash
        df_temp = df_temp.rename(columns={'EEPS_CURR_YR': ticker + '_EEPS_CURR_YR' , 'PX_LAST': ticker + "_PX_LAST" })
        df = df.join(df_temp)  # use default how = 'left'

        if ticker == 'M7EU': # drop dates on which SPY did not trade
            df = df.dropna(subset=["M7EU_PX_LAST"])

    return df

def normalize_data(df):
    """Normalize the stock price using the first row of the dataframe"""
    return df/df.ix[0,:]

def plot_data(df, stock_name,title = "Stock prices", xlabel = "Date", yLabel = "Price"):
    """plot stock prices"""
    fig , ax1 = plt.subplots()

    # plot rolling EPS vs Date on Primary axis
    ax1.set_title(stock_name + ' EPS Trend over time')
    color = 'tab:blue'
    ax1.set_xlabel("Dates")
    ax1.set_ylabel("90 Days Rolling EPS", color=color)
    #ax1.axis(ymin = 0, ymax = 15) # set the y axis limits
    ax1.stackplot(df.index.values,df[stock_name + '_90D_ROLL_EPS'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    #ax1.tick_params(axis='x', labelsize=5)

    
    # Create a secondary axis and plot daily returns on that with X axis bein date
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis 
    color = 'tab:red'
    ax2.set_ylabel('Returns', color=color)
    # ax2.axis(ymin = -0.5, ymax = 0.15) # set the y axis limits
    ax2.plot( df.index.values,df[stock_name + '_AVG_PERIODIC_RETURN'], color=color)
    # ax2.plot(df.index.values,df['SOLB_FLG_WITHIN_TODAY_EPS_BAND'], color='tab:green')
    ax2.tick_params(axis='y', labelcolor=color)

    # Identify dates which has EPS in same range as Todays's EPS
    dates_matching_todays_eps = df[df[stock_name + "_FLG_WITHIN_TODAY_EPS_BAND"]==1].index.values
    for date in dates_matching_todays_eps:
    	plt.axvline(x=date, color='tab:green', linestyle='-')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig( "output/"+ stock_name + '.png')
    plt.show() # must be called to show plots in some environment



def compute_periodic_returns(df,period):
	"""Computes return for a period where period can be 1 day, 2 days ..30 days, 90 days"""
	# daily_returns[1:] = (df[1:] / df[:-1].values) - 1
	# daily_returns.ix[0, :] = 0  # set daily returns for day 0 as 0
	periodic_returns = df.copy()  # copy Given Dataframe to match size and scale
	periodic_returns[period:] = (df[period:] / df[:-period].values) -1
	periodic_returns.iloc[0:period] = 0  # set periodic returns for day before the period day as 0
	return periodic_returns



def is_within_today_eps_band(eps,eps_upper_band,eps_lower_band):
 	""" Checks if the Rolling EPS is within todays Rolling EPS band"""
 	
 	if (eps >= eps_lower_band and eps <= eps_upper_band) :
 		# print(eps,eps_upper_band,eps_lower_band)
 		return 1
 	else :
 		return 0


if __name__ == "__main__":


    ## Take All data since Jan 2010 till 30 aug 2018
    start_date = '2014-03-11'
    end_date = '2018-09-26'
    dates = pd.date_range(start_date,end_date)

    # Read in more stocks
    symbols = ['SOLB','AZN', 'EOFP','MLFP','PSNLN']
    #symbols = ['SOLB']

    for symbol in symbols:
	    # Get the combined data in a datafram
	    df = get_data(symbol,dates)
	    #print(df)


	    # Get 90 Days Rolling EPS
	    rolling_days = 67
	    df[str(symbol) + '_90D_ROLL_EPS'] = df[str(symbol) + '_EEPS_CURR_YR'].rolling(rolling_days).mean()
	    # print(df)

	    # Calculate periodic returns
	    periods = pd.Series(range(1,rolling_days + 1))


	    for period in periods:
	    	df[symbol + '_'+ str(period) + 'DAY_RETURN'] = compute_periodic_returns(df[str(symbol) + '_EEPS_CURR_YR'],period)

	    # print(df.head())
	    # df.to_csv('SOLB_TEMP.csv')

	    # Get average periodic return at a day level
	    start_col_index = 4
	    end_col_index = start_col_index + rolling_days
	    df[str(symbol) + '_AVG_PERIODIC_RETURN'] = df.iloc[ : ,start_col_index:end_col_index].mean(axis=1)
	    # print(df.head())


	    # Get a flag if Rolling EPS is between the certain % of Todays Rolling EPS
	    eps_band_perc = 0.05
	    todays_periodic_avg_returns = df.iloc[-1 ,df.columns.get_loc(str(symbol) + '_AVG_PERIODIC_RETURN')]
	    eps_return_lower_band = (1 - eps_band_perc)*todays_periodic_avg_returns
	    eps_return_upper_band = (1 + eps_band_perc)*todays_periodic_avg_returns
	 
	    # Set flag as 1 if periodic returns is between upper band and lower band
	    df[str(symbol) + '_FLG_WITHIN_TODAY_EPS_BAND'] = df[str(symbol) + '_AVG_PERIODIC_RETURN'].apply(is_within_today_eps_band, args=(eps_return_upper_band,eps_return_lower_band))
	    # print(df.iloc[df["SOLB_FLG_WITHIN_TODAY_EPS_BAND"]==1])

	    # Make the Graph
	    # plot_data(df['SOLB_90D_ROLL_EPS'], title = "90 Days Rolling EPS", xlabel = "Date", yLabel = "Return")
	    plot_data(df, str(symbol))

	    
	    # print(df.head())
	    df.to_csv("output/" +str(symbol)  + '_TEMP.csv')
    
    





