
import os

from togetfun.third.maths import Jsp_API
from datetime import datetime, timedelta
import pandas as pd

print("国内外历史高频股票期货等数据下载前往“ToGetFun”网站获取获取（网址：togetfun.top）")
print("--------------------")

import sys
import json
import requests

bTest = 0
debug = 0
dat = pd.DataFrame()
time_close1 = datetime.strptime("11:30:00", '%H:%M:%S')
time_open1 = datetime.strptime("9:30:00", '%H:%M:%S')
time_close2 = datetime.strptime("15:00:00", '%H:%M:%S')
time_open2 = datetime.strptime("13:00:00", '%H:%M:%S')

bInit = 0
api = Jsp_API()

def print_info(e):
    print(e)
    print(dat.iloc[44, 0])


def get_now_time(bStr = 0):
    utc_now = datetime.utcnow()
    beijing_time = utc_now + timedelta(hours=8)
    strNow = beijing_time.strftime('%H.%M.%S.%f')[:-3]
    if bStr:
        return strNow
    else:
        return datetime.strptime(strNow, '%H.%M.%S.%f')



def Init():
    global bInit
    if bInit == 1:
        return 1

    str_ip = "122.51.232.182"
    str_port = "7709"
    api.connect(str_ip, int(str_port))
    bInit = 1
    # 将内容转换为字符串列表
    """
    url = f"http://localhost:5000/api/auth/token?token=test123&type=10001"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get('success') == True and 'data' in data:
            ip_port = data['data'].get('ip_port')
            str_ip = ip_port.split(':')[0]
            str_port = ip_port.split(':')[1]
            api.connect(str_ip, int(str_port))
            bInit = 1
    else:
        print("连接失败，请稍后重试")
    """
    return api



def __select_market_code(code):
    code = str(code)
    if '.' in code:
        if code.split('.')[0] == 'SZ':
            return 0
        elif code.split('.')[0] == 'SH':
            return 1
        else:
            return 2
    else:
        if code[0] in ['5', '6', '9'] or code[:3] in ["009", "126", "110", "201", "202", "203", "204"]:
            return 1
        if code[0] in ['8']:
            return 2
        return 0

def __select_code(code):
    code = str(code)
    if '.' in code:
        return code.split('.')[1]
    else:
        return code

def get_code(market):
    list_df = []
    i = 0
    if market == 1:
        i = 1000
    while 1:
        df = api.to_df(api.get_security_list(market, i))
        if len(df) <= 1 :
            break

        if len(df) > 0:
            df00 = df[df['code'].str[:2] == '00']
            df30 = df[df['code'].str[:2] == '30'] #300开头获取不到
            df60 = df[df['code'].str[:2] == '60']
            df68 = df[df['code'].str[:2] == '68']

            list_df.append(df00)
            list_df.append(df30)
            list_df.append(df60)
            list_df.append(df68)

        i = i + 1000
    df = ''
    if len(list_df) > 0:
        df = pd.concat(list_df)
        df = df.drop(['volunit', 'decimal_point'], axis=1)
        df = df.reset_index(drop=True)
    return df

def get_recent_data(code, start_date, end_date, period, index=False):
    Init()
    periodDic = {'1min' : 8, '5min': 0, '15min': 1, '30min': 2, '1h': 3, 'D': 4, 'W': 5, 'M': 6}

    date1 = datetime.strptime(start_date, "%Y-%m-%d")
    date2 = datetime.now()
    # 计算日期差异
    n = (date2 - date1).days + 1

    date_list = []
    for i in range(n):
        if index == False:
            df_tem = api.to_df(api.get_security_bars(periodDic[period], __select_market_code(code), __select_code(code), i * 800, 800))
        else:
            df_tem = api.to_df(api.get_index_bars(periodDic[period], __select_market_code(code), __select_code(code), i * 800, 800))
        if df_tem.empty:
            return df_tem
        time_tem = df_tem.iloc[0].loc['datetime']
        time2 = datetime.strptime(time_tem, "%Y-%m-%d %H:%M")

        date_list.insert(0, df_tem)

        if time2 < date1:
            break

    data = pd.concat(date_list)

    if data.empty:
        return data
    data = data.assign(date=data['datetime'].apply(lambda x: str(x)[0:10])).assign(code=__select_code(code))\
        .set_index('date', drop=False, inplace=False)\
        .drop(['year', 'month', 'day', 'hour', 'minute'], axis=1)[start_date:end_date]

    return data.assign(date=data['date'].apply(lambda x: str(x)[0:10]))

def get_index_data(code, start_date, end_date, period):
    return get_recent_data(code, start_date, end_date, period, index=True)

def get_hq_dt():
    return sys.gettrace() is not None

def get_real_hq(all_stock, notify=False, bUpdateCode=False):
    if len(all_stock) > 80:
        print(dat.iloc[47, 0])
        return pd.DataFrame()
    Init()
    list_all = []
    for c in all_stock:
        list_all.append((__select_market_code(c), __select_code(c)))
    stocks = api.get_security_quotes(list_all)
    if stocks == None :
        if notify == True:
            print(dat.iloc[48, 0])
        return pd.DataFrame()
    i = 0
    df_list = []
    while i < len(stocks):
        df1 = pd.DataFrame(stocks[i])
        if df1.empty:
            continue
        df_list.append(df1)
        i = i + 1
    if len(df_list) == 0:
        return pd.DataFrame()
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df = combined_df.drop(
        ['market', 'active1', 'last_close', 'open', 'high', 'low', 'reversed_bytes0', 'reversed_bytes1',
         'cur_vol', 'reversed_bytes2', 'reversed_bytes3', 'reversed_bytes4', 'reversed_bytes5',
         'reversed_bytes6', 'reversed_bytes7', 'reversed_bytes8', 'reversed_bytes9',
         'active2'], axis=1)

    if bUpdateCode:
        return combined_df
    combined_df['servertime'] = get_now_time(1)
    now = get_now_time()
    if now < time_open1 or now > time_close2 or (now>time_close1 and now<time_open2):
        return pd.DataFrame()
    combined_df.columns = ['代码','价格','时间','成交量','成交额','总卖','总买','买一价','卖一价','买一量','卖一量',
                           '买二价','卖二价','买二量','卖二量','买三价','卖三价','买三量','卖三量','买四价','卖四价','买四量','卖四量','买五价','卖五价','买五量','卖五量',]
    return combined_df

def get_real_kzz(all_stock):
    df = get_real_hq(all_stock)
    if len(df) == 0:
        return df

    df['价格'] = df['价格'] * 0.01
    df['买一价'] = df['买一价'] * 0.01
    df['买二价'] = df['买二价'] * 0.01
    df['买三价'] = df['买三价'] * 0.01
    df['买四价'] = df['买四价'] * 0.01
    df['买五价'] = df['买五价'] * 0.01
    df['卖一价'] = df['卖一价'] * 0.01
    df['卖二价'] = df['卖二价'] * 0.01
    df['卖三价'] = df['卖三价'] * 0.01
    df['卖四价'] = df['卖四价'] * 0.01
    df['卖五价'] = df['卖五价'] * 0.01
    return df

def get_all_real_hq():
    codes_list = []
    hq_list = []
    script_path = __file__
    file_path, file_name = os.path.split(script_path)
    df_code = pd.read_csv(file_path + '//code.csv', encoding='utf-8', dtype={'code': str})
    for i in range(len(df_code)):
        code = str(df_code.iloc[i, 0])
        codes_list.append(code)
        if len(codes_list) == 80:
            df = get_real_hq(codes_list)
            hq_list.append(df)
            codes_list = []
    df = get_real_hq(codes_list)
    hq_list.append(df)
    df = pd.concat(hq_list)
    df = df.reset_index(drop=True)
    if len(df) == 0:
        return df
    df['servertime'] = get_now_time(1)
    return df


def get_tick(code, date):
    Init()
    date = int(date.strftime("%Y%m%d"))
    df1 = api.to_df(api.get_history_transaction_data(__select_market_code(code), __select_code(code), 0, 5000, date))
    df2 = api.to_df(api.get_history_transaction_data(__select_market_code(code), __select_code(code), 2000, 5000, date))
    df3 = api.to_df(api.get_history_transaction_data(__select_market_code(code), __select_code(code), 4000, 5000, date))
    df = pd.concat([df3, df2, df1], ignore_index=True)
    df.columns = ['时间', '价格', '成交量', '买卖方向']

    return df


#--------------------------


# --------------jsp---------
def history_stock_data(code, start_date, end_date, period):
    try:
        df = get_recent_data(code, start_date, end_date, period)
        df.columns = ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '日期', '日', '代码']
        df = df[['代码','日期','开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额']]
        return df
    except Exception as e:
        print_info(e)


def history_etf_data(code, start_date, end_date, period):
    try:
        df = get_recent_data(code, start_date, end_date, period)
        df.columns = ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '日期', '日', '代码']
        df = df[['代码','日期','开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额']]
        return df
    except Exception as e:
        print_info(e)


def history_kzz_data(code, start_date, end_date, period):
    try:
        df = get_recent_data(code, start_date, end_date, period)
        df.columns = ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '日期', '日', '代码']
        df = df[['代码','日期','开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额']]
        return df
    except Exception as e:
        print_info(e)


def history_index_data(code, start_date, end_date, period):
    try:
        df = get_index_data(code, start_date, end_date, period)
        df.columns = ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '日期', '上涨数量', '下跌数量', '日',
                      '代码']
        df = df[['代码','日期','开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额', '上涨数量', '下跌数量']]
        return df
    except Exception as e:
        print_info(e)



def history_stock_tick(code, date):
    try:
        return get_tick(code, date)
    except Exception as e:
        print_info(e)


def history_etf_tick(code, date):
    try:
        return get_tick(code, date)
    except Exception as e:
        print_info(e)


def history_kzz_tick(code, date):
    try:
        return get_tick(code, date)
    except Exception as e:
        print_info(e)


def history_index_tick(code, date):
    try:
        return get_tick(code, date)
    except Exception as e:
        print_info(e)




def realtime_stock_data(all_stock):
    try:
        return get_real_hq(all_stock)
    except Exception as e:
        print_info(e)


def realtime_etf_data(all_stock):
    try:
        return get_real_hq(all_stock)
    except Exception as e:
        print_info(e)


def realtime_kzz_data(all_stock):
    try:
        return get_real_kzz(all_stock)
    except Exception as e:
        print_info(e)


def realtime_index_data(all_stock):
    try:
        return get_real_hq(all_stock)
    except Exception as e:
        print_info(e)





###########

"""
df = history_stock_data('SH.600000', '2025-09-10', '2025-09-16', '5min') # 返回值为dataframe格式

df.to_csv("D:\\tem\\0916\\600000_tdx_5_stock_k_data.csv", index=False)
#print(df) # 可以打印数据
with pd.option_context('display.max_columns', None):
    pd.set_option('display.width', 1000)
    print(df)

"""