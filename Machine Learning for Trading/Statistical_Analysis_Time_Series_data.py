import os
import pandas as pd
import matplotlib.pyplot as plt


def symbol_to_path(symbol, base_dir="data"):
    """Return CSV file path given a ticker symbol"""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))

def get_data(symbols, dates):
    """Read stock data(adjusted close) for given symbols from CSV files"""
    df = pd.DataFrame(index=dates)
    if 'SPY' not in symbols: # Add SPY for reference, if absent
        symbols.insert(0, 'SPY')

    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol),index_col='Date',
                              parse_dates=True, usecols = ["Date", "Adj Close"], na_values = ['nan'])
        # Rename to prevent clash
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df = df.join(df_temp)  # use default how = 'left'

        if symbol == 'SPY': # drop dates on which SPY did not trade
            df = df.dropna(subset=["SPY"])

    return df

def normalize_data(df):
    """Normalize the stock price using the first row of the dataframe"""
    return df/df.ix[0,:]

def plot_data(df, title = "Stock prices", xlabel = "Date", yLabel = "Price"):
    """plot stock prices"""
    ax = df.plot(title=title, fontsize = 5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(yLabel)
    plt.show() # must be called to show plots in some environment

def plot_selected(df, columns, start_index, end_index):
    """Plot the desired columns over index values in the given range."""
    plot_data(df.ix[start_index:end_index,columns], title = "Selected Data")

def plot_bollinger_band(df):
    """
    : This computes the bollinger band
    :param df:
    :return:
    """

    # Compute rolling mean using a 20 day windows
    rm_SPY = df.rolling(20).mean()

    # compute Rolling STD
    rstd_SPY = df.rolling(20).std()

    # Compute upper and lower band
    upper_band, lower_band = rm_SPY * (1 + 2 * rstd_SPY), rm_SPY * (1 - 2 * rstd_SPY)

    # Plot SPY data, retain matplotlib axis object
    ax = df.plot(title="Bollinger Band", label="SPY")
    # Add rolling mean to same plot
    rm_SPY.plot(label='Rolling mean', ax=ax)
    # Add  band to the same plot
    upper_band.plot(label="Upper Band", ax=ax)
    lower_band.plot(label="Lower Band", ax=ax)

    # Add Axis Label and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    plt.show()

def compute_daily_returns(df):
    daily_returns = df.copy()  # copy Given Dataframe to match size and scale
    daily_returns[1:] = (df[1:] / df[:-1].values) - 1
    daily_returns.ix[0, :] = 0  # set daily returns for day 0 as 0
    return daily_returns

def compute_cumulative_returns(df):
    cumulative_returns = df.copy()  # copy Given Dataframe to match size and scale
    cumulative_returns[1:] = (df[1:] / df.ix[0,:].values) - 1
    cumulative_returns.ix[0, :] = 0  # set daily returns for day 0 as 0
    return cumulative_returns

if __name__ == "__main__":


    ## Take All data since Jan 2010 till 30 aug 2018
    start_date = '2010-01-01'
    end_date = '2012-12-31'
    dates = pd.date_range(start_date,end_date)

    # Read in more stocks
    # symbols = ['SPY','GOOG','IBM','GLD']
    symbols = ['SPY']

    # Get the combined data in a datafram
    df = get_data(symbols,dates)

    # # Plot the normalized data
    # plot_data(normalize_data(df))
    #
    # # Plot the Bollinger band
    #
    plot_bollinger_band(df["SPY"])
    #
    # # Calculate Daily Returns
    daily_returns = compute_daily_returns(df)
    plot_data(daily_returns,title="Daily Returns",xlabel="Date",yLabel="Percentage")
    #
    # # Calculate Cumulative Returns # THE GRAPH IS NOT PROPOER
    # cumulative_returns = compute_cumulative_returns(df)
    # plot_data(cumulative_returns, title="Cumulative Returns", xlabel="Date", yLabel="Percentage")








