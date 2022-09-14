import datetime as dt
import json
import requests as rq
import pandas as pd
import numpy as np
import pybit as pbt
from pybit import usdc_options
import warnings
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def get_option_desk(with_time=False):
    
    t1 = dt.datetime.now().timestamp()
    session = usdc_options.HTTP(
    endpoint='https://api.bybit.com', 
    api_key='...',
    api_secret='...'
    )
    
    key_symbols = 'https://api-testnet.bybit.com/option/usdc/openapi/public/v1/symbols'
    data = rq.get(key_symbols).json()
    dataList = []
    
    for i in data['result']['dataList']:
        dataList.append(i)
    
    symbols = []
    for j in dataList:
        symbols.append(j['symbol'])
        
    df=[]
    for k in symbols:
        df.append(session.latest_information_for_symbol(symbol=k)['result'])
    df1=pd.json_normalize(df) #привожу к формату dataframe
    #Удаляю строки с пустыми значениями:
    df1.replace('',np.nan,inplace=True)
    df1.dropna(subset='symbol', inplace=True)

    df2=df1[['symbol','bid','ask','markPrice','markPriceIv']]
    df2[['asset','contract_date','strike','option_type']]=df2['symbol'].str.split('-',expand=True)
    df2.drop('symbol', axis=1,inplace=True)
    
    df = df2[df2['bid'] != '']
    df.reset_index(inplace=True)
    for i in range(len(df)):
        df['bid'][i] = int(df['bid'][i])
        df['ask'][i] = int(df['ask'][i])
        df['strike'][i] = int(df['strike'][i])
        df['markPrice'][i] = float(df['markPrice'][i])
        df['markPriceIv'][i] = float(df['markPriceIv'][i])

    df.set_index('strike',inplace=True)        
    desk = dict()

    for typ in set(df['option_type']):
        tmp = df[df['option_type'] == typ]
        for date in set(tmp['contract_date']):
            desk[typ + date] = tmp[tmp['contract_date'] == date]
    
    t2 = dt.datetime.now().timestamp()
    
    if with_time:
        print('Processing time:', t2 - t1)
    
    return desk
