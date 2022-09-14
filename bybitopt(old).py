import datetime as dt
import json
import requests as rq
import pandas as pd
import numpy as np

def get_option_desk(with_time=False):
    
    t1 = dt.datetime.now().timestamp()
    
    key_symbols = 'https://api-testnet.bybit.com/option/usdc/openapi/public/v1/symbols'
    data = rq.get(key_symbols).json()
    dataList = []
    
    for i in data['result']['dataList']:
        dataList.append(i)
    
    symbols = []
    for j in dataList:
        symbols.append(j['symbol'])
        
    info = []
    key_info='https://api-testnet.bybit.com/option/usdc/openapi/public/v1/tick?symbol='

    for k in symbols:
        info.append(rq.get(key_info+k).json()['result'])
        
    df=pd.json_normalize(info)

    df = df.dropna()[['symbol','bid','ask','markPrice','markPriceIv']]
    df[['asset','contract_date','strike','option_type']] = df['symbol'].str.split('-',expand=True)
    df.drop('symbol', axis=1,inplace=True)
    df = df[df['bid'] != '']

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
