# Import libraries
import datetime as dt
from datetime import datetime as dtm
import requests as rq
import pandas as pd
import gzip
import shutil
import os

def get_historic_data(date, years=1, with_time=False):
    
    if date<'2020-10-01':
        return(print('Too early! First historic date available is 2019-10-01'))

    dtm_end=dtm.strptime(date,'%Y-%m-%d')
    dtm_start=dtm_end.replace(year=dtm_end.year-years)
    
    #Создаю список дат за последний год
    cal=pd.date_range(start=dtm_start,end=dtm_end)
    
    t1=dt.datetime.now().timestamp()
    for i in cal:
        doc='BTCUSD'+str(i)[0:10]+'_index_price.csv.gz'
        a=rq.get('https://public.bybit.com/spot_index/BTCUSD/'+doc, allow_redirects=True)
        #download the data
        open(doc, 'wb').write(a.content)
        #unzip them
        with gzip.open(doc, 'rb') as f_in:
            with open(doc[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        #making DataFrame
        try:
            df_next=pd.read_csv(doc[:-3]) #if we already created df
            union=pd.concat([df,df_next])
            df=union
        except NameError: #if df wasn't mentioned
            df=pd.read_csv(doc[:-3])
        #remove unnecessary files:
        os.remove(doc)
        os.remove(doc[0:-3])
        
    t2=dt.datetime.now().timestamp()
    #print('Processing time:', t2 - t1) #200+ секунд (зависит от интернета)
    
    df['datetime']=pd.to_datetime(df["start_at"], unit="s")
    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True, drop=True)
    
    if with_time:
        print('Processing time:', t2 - t1)
    return(df)