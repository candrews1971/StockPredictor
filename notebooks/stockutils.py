import os
import pandas as pd


DATA_FILE = 'AAPL_Advanced.csv'
DATA_PATH = os.path.join("..","data", "raw", DATA_FILE)

FEATURES_TO_USE = ['pct_Diff_from_6_day_SMA', 'Slope_6_day_SMA', 'Slope_4_day_SMA','CHLI_1Y', 'CHLI_1M', 'CHLI_2W',
       'CHLI_1W', 'ADV_Issues','ADV_Vol','ADV_Issues_Comp', 'ADV_Vol_Comp', 'ImpVol', 'daysToEarnings',
       '2yr_pct_chg', '10yr_pct_chg', '10yr_2yr_diff',
       '10_2_diff_pct_chg', '10_day_SMA', '20_day_SMA', '10_day_SMA_slope',
       '20_day_SMA_slope', 'price_chg', 'vix_chg']

#Columns of interest might include the un-stationarized versions, for later visualization
COLUMNS_OF_INTEREST = ['close','vix','2yr_Yield', '10yr_Yield']

TARGETS = ["ExactBestMajorReversals","DayAfterMajorReversal","4_days_ahead_TARGET", "5pct_20day_TARGET","5pct_10day_TARGET", "2_5pct_5day_TARGET" ] 

def import_stock_csv(filename, data_path=DATA_PATH, columnsToUse=FEATURES_TO_USE, target="DayAfterMajorReversal", colsofinterest=COLUMNS_OF_INTEREST):
    """load the stock data

    Not the most flexible import, but will do for this case... 
    Needs improvements to make it flexible for ongoing future use.
    
    Parameters
    ----------
    filename  : 
        name of the csv file to load
    data_path :
        (Default value = DATA_PATH)
    columnsToUse: 
        list of column names to keep for final
        defaults to FEATURES_TO_USE
    target:
        the name of the target column.  Can be one of the provided, or custom from your csv file
    Returns:
    
    -------
    """
    #read the csv file
    stockdf = pd.read_csv(DATA_PATH, index_col=0)

    # update data types for targets (all categorical)
    stockdf.ExactBestMajorReversals = stockdf.ExactBestMajorReversals.astype("category")
    stockdf.DayAfterMajorReversal = stockdf.DayAfterMajorReversal.astype("category")
    stockdf['4_days_ahead_TARGET'] = stockdf['4_days_ahead_TARGET'].astype("category")
    stockdf["5pct_10day_TARGET"] = stockdf["5pct_10day_TARGET"].astype("category")
    stockdf["5pct_20day_TARGET"] = stockdf["5pct_20day_TARGET"].astype("category")
    stockdf["2_5pct_5day_TARGET"] = stockdf["2_5pct_5day_TARGET"].astype("category")
    stockdf["SellIfNotBuy"] = stockdf["SellIfNotBuy"].astype("category")
    stockdf["TwoStateMajorReversals"] = stockdf["TwoStateMajorReversals"].astype("category")

    # take out the commas in some numbers so we can make them numerical instead of object type
    # TODO: do this for all appropriate columns
    stockdf.advancedVolumeComp = stockdf.advancedVolumeComp.str.replace(",","")
    stockdf.declinedVolumeComp = stockdf.declinedVolumeComp.str.replace(",","")
    stockdf.newLows1W = stockdf.newLows1W.str.replace(",","")

    #convert them to numerical data
    stockdf.advancedVolumeComp = stockdf.advancedVolumeComp.astype(int)
    stockdf.declinedVolumeComp = stockdf.declinedVolumeComp.astype(int)
    stockdf.newLows1W = stockdf.newLows1W.astype(int)

    #fill missing data -so happens we just want interpolation, not fillna(ffill)
    # TODO: just do this for everything that we can, regardless of the actual data state
    stockdf.vix = stockdf.vix.interpolate()
    stockdf['2yr_Yield'].interpolate(inplace=True)
    stockdf['10yr_Yield'].interpolate(inplace=True)
    stockdf.newHighs2W = stockdf.newHighs2W.interpolate()

    # regenerate certain columns
    stockdf['2yr_pct_chg'] = stockdf['2yr_Yield'].pct_change()
    stockdf['10yr_pct_chg'] = stockdf['10yr_Yield'].pct_change()
    stockdf['10yr_2yr_diff'] = stockdf['10yr_Yield'] - stockdf['2yr_Yield']
    stockdf['10_2_diff_pct_chg']= stockdf['10yr_2yr_diff'].pct_change()

    #add new derived features
    for offset in [10, 20]:
        colname = "{}_day_SMA".format(offset)
        stockdf[colname] = stockdf['close'].rolling(offset).mean()

    stockdf['10_day_SMA_slope'] = stockdf['10_day_SMA'].pct_change()
    stockdf['20_day_SMA_slope'] = stockdf['20_day_SMA'].pct_change()

    stockdf['price_chg'] = stockdf['close'].pct_change()
    stockdf['vix_chg'] = stockdf['vix'].diff()
    stockdf['Slope_4_day_SMA'] = stockdf['4_day_SMA'].pct_change()
    stockdf['Slope_6_day_SMA'] = stockdf['6_day_SMA '].pct_change()

    #drop columns
    stockdf.drop(columns=['PutCallRatio', 'daysToDividend'], inplace=True)
    stockdf.dropna(inplace=True)

    featuresdf = stockdf[columnsToUse] 
    targetdf = stockdf[[target]].copy()
    targetdf["Target"] = targetdf[[target]]
    targetdf.drop(columns=[f"{target}"], inplace=True)
    #targetdf = targetdf.rename(columns={f"{target}":'Target'}, inplace=True)
    interestdf = stockdf[colsofinterest]

    return featuresdf, targetdf, interestdf

def plot_feature_importances(X_train, estimator ):
    feature_importances = list(zip(X_train.columns, estimator.feature_importances_))
    fi = pd.Series(estimator.feature_importances_, index=X_train.columns)
    sorted_imp = pd.DataFrame(fi.sort_values(ascending=True), columns=['importance'])
    sorted_imp.plot(kind='barh',color="red")


import math




def calculate_total_gains_bs(df, init_value, init_price, transaction_cost_fixed=0.0  ):
    price = init_price
    num_shares_owned = 0
    gain = 0.0
    cash_balance = init_value
    for idx, row in df.iterrows():
        price = df.loc[idx,'close']#price + (price * row['price_change_pct'])
        if row["Target"] == 'BUY' or row['Target'] == 0:
            max_shares = math.floor(cash_balance/price)
            if max_shares > 0:
                num_shares_owned += max_shares
                cash_balance = cash_balance - (max_shares*price)
                print("Buying {} shares for {:0.2f}. Remaining Balance: {}".format(max_shares, price, cash_balance))
        elif row["Target"] == 'SELL' or row['Target']== 1:
            cash_balance = cash_balance + (num_shares_owned * price)
            if num_shares_owned != 0:
                print("Selling all shares for {:0.2f}, cash balance: ${}".format(price, cash_balance))
            num_shares_owned = 0
    #sell at the end for gain calculation if we are holding stock
    cash_balance = cash_balance + (num_shares_owned * price)   
    print("Selling all remaining held shares, cash balance: ${} ***********************".format(cash_balance))
    roi = cash_balance - init_value
    return roi

import math

def calculate_total_gains_bhs(df, init_value, init_price, transaction_cost_fixed=0.0  ):
    price = init_price
    num_shares_owned = 0
    gain = 0.0
    cash_balance = init_value
    for idx, row in df.iterrows():
        price = df.loc[idx,'close']#price + (price * row['price_change_pct'])
        if row["Target"] == 'BUY' or row['Target'] == 0:
            max_shares = math.floor(cash_balance/price)
            if max_shares > 0:
                num_shares_owned += max_shares
                cash_balance = cash_balance - (max_shares*price)
                print("Buying {} shares for {:0.2f}. Remaining Balance: {}".format(max_shares, price, cash_balance))
        elif row["Target"] == 'SELL' or row['Target']== 2:
            cash_balance = cash_balance + (num_shares_owned * price)
            if num_shares_owned != 0:
                print("Selling all shares for {:0.2f}, cash balance: ${}".format(price, cash_balance))
            num_shares_owned = 0
    #sell at the end for gain calculation if we are holding stock
    cash_balance = cash_balance + (num_shares_owned * price)   
    print("Selling all remaining held shares, cash balance: ${} ***********************".format(cash_balance))
    roi = cash_balance - init_value
    return roi