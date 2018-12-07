import os
import pandas as pd
import datetime as dt
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

def plot_data(df, title = "Stock prices"):
    """plot stock prices"""
    ax = df.plot(title=title, fontsize = 5)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show() # must be called to show plots in some environment

def plot_selected(df, columns, start_index, end_index):
    """Plot the desired columns over index values in the given range."""
    plot_data(df.ix[start_index:end_index,columns], title = "Selected Data")


if __name__ == "__main__":


    ## Take All data since Jan 2010 till 30 aug 2018
    start_date = '2010-01-01'
    end_date = '2018-08-31'
    dates = pd.date_range(start_date,end_date)

    # Read in more stocks
    symbols = ['GOOG','IBM','GLD']

    # Get the combined data in a datafram
    df = get_data(symbols,dates)

    # example of row slicing
    # print(df.ix['2010-01-01':'2010-01-31'] # data for month of jan 2010)

    # example of column slicing
    # print(df['GOOG') # this selects data for google
    # print(df[['GOOG', 'IBM']]) # multiple column selection

    # example of row column slicing
    # print(df.ix['2010-01-01':'2010-01-31',['GOOG', 'IBM']]) # Data for Jan 2010 for Google and IBM

    plot_data(normalize_data(df))





