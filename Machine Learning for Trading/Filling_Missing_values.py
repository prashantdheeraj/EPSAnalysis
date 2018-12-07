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

def plot_data(df, title = "Stock prices"):
    """plot stock prices"""
    ax = df.plot(title=title, fontsize = 5)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show() # must be called to show plots in some environment

def plot_selected(df, columns, start_index, end_index):
    """Plot the desired columns over index values in the given range."""
    plot_data(df.ix[start_index:end_index,columns], title = "Selected Data")


def fill_missing_values(df):
    """Fills the missing value with Forward fill and then backward fill"""
    df.fillna(method="ffill", inplace=True)
    df.fillna(method="bfill", inplace=True)

    return df


if __name__ == "__main__":


    ## Take All data since Jan 2010 till 30 aug 2018
    start_date = '2005-12-31'
    end_date = '2014-12-07'
    dates = pd.date_range(start_date,end_date)

    # Read in more stocks
    symbols = ['JAVA','FAKE1', 'FAKE2']

    # Get the combined data in a datafram
    df = get_data(symbols,dates)

    #Fill missing value with forward fill first and then back fill
    plot_data(fill_missing_values(df))




