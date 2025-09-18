""" 
1. py tasks\stock_market_data_tasks\nse_stock_market.py
"""

import os, sys
from urllib import response
from wsgiref import headers
import pandas as pd
import requests
from urllib3 import Retry

# parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
# sys.path.append(parentdir)

niftyTypes = ["NIFTY 50", "NIFTY NEXT 50", "NIFTY MIDCAP SELECT", "NIFTY BANK", "NIFTY FINANCIAL SERVICES"]
nifty_legends = [['NIFTY', 'NIFTY 50'], ['BANKNIFTY', 'BANK NIFTY'], ['NIFTYNEXT50', 'NIFTY NEXT 50'], ['SecGtr20', 'Securities > Rs 20'], ['SecLwr20', 'Securities < Rs 20'], ['FOSec', 'F&O Securities'], ['allSec', 'All Securities']] 
monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class NSE():
    # setup nse headers
    
    nse_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Accept-Language': 'en,gu;q=0.9,hi;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'accept-encoding': 'gzip, deflate, br'
    }
    
    # lists of nse apis
    nse_apis = {
        "nse_base_url": "https://www.nseindia.com",
        "company_meta_info_url": "https://www.nseindia.com/api/equity-meta-info?symbol={}",
        # "allsec_gainers": "/api/liveanalysis/gainers/allSec",
        # "allsec_loosers": "/api/liveanalysis/loosers/allSec",
        "index_gainers": "/api/live-analysis-variations?index=gainers",
        "index_loosers": "/api/live-analysis-variations?index=loosers",
        "nse_etf": "/api/etf",
        "nse_fii_dii": "/api/fiidiiTradeReact",
        # "allcontracts": "api/equity-stock?index=allcontracts",
        "nifty50_marketstate_daily": "/api/marketStatus",
        "nse_index_daily": "/api/equity-stockIndices?index={}",
        "nse_index_symbol": "/api/index-names",
        # "test": "/api/search/autocomplete"
    }
    
    index_gainers_loosers_col = ["symbol", "ltp", "prev_price", "open_price", "high_price", "low_price", "trade_quantity", "series", "net_price", "turnover", "market_type", "ca_ex_dt", "ca_purpose", "perChange"]
    
    
    # setup nse sessions to call nse apis
    def __init__(self):
        self.session = requests.Session()
        self.request = self.session.get(self.nse_apis["nse_base_url"], headers=self.nse_headers, timeout=5)
        self.cookies = dict(self.request.cookies)
        
    def company_meta_details(company_symbol: str) -> dict:
        url = nse_company_meta_info_url.format(company_symbol)
        
        session = requests.Session()
        request = session.get(nse_base_url, headers=headers, timeout=5)
        cookies = dict(request.cookies)
        response = session.get(url, headers=headers, timeout=5, cookies=cookies)
        out = response.json()
        return out
    
    def get_marketstate_daily(self):
        url = self.nse_apis["nse_base_url"] + self.nse_apis["nifty50_marketstate_daily"]
        response = self.session.get(url, headers=self.nse_headers, timeout=5, cookies=self.cookies)
        if response.status_code == 200:
            # out_df = pd.DataFrame(response.json().get("marketcap"))
            out_df = pd.DataFrame(response.json().get("marketState"))
            out_df = out_df.loc[out_df["market"].isin(["Capital Market", "currencyfuture"]), ["market", "tradeDate", \
                                                                                              "last", "variation", \
                                                                                              "percentChange"]]
            return out_df
        else:
            return {"error": "Failed to fetch data"}
    
    def get_nifty50_daily_data(self):
        index_symbol = "NIFTY 50".replace(" ", "%20")
        columns = ["symbol", "open", "dayHigh", "dayLow", "lastPrice", "previousClose", "change", "yearHigh", "yearLow",
                   "totalTradedVolume", "lastUpdateTime"]
        url = self.nse_apis["nse_base_url"] + self.nse_apis["nse_index_daily"].format(index_symbol)
        try:
            response = self.session.get(url, headers=self.nse_headers, timeout=5, cookies=self.cookies)
            # response.raise_for_status()
        except Exception as e:
            print(f"error raised, {e}")
        else:
            out = response.json()
            lastUpdateTime =  out.get("metadata").get("timeVal")
            out_df = pd.DataFrame(out.get("data")).loc[:, columns]
            out_df["lastUpdateTime"] = lastUpdateTime
            return out_df
    
    def get_index_symbol(self):
        url = self.nse_apis["nse_base_url"] + self.nse_apis["nse_index_symbol"]
        response = self.session.get(url, headers=self.nse_headers, timeout=5, cookies=self.cookies)
        if response.status_code == 200:
            out = response.json()
            out_dict = dict()
            for i in out.get("stn"):
                out_dict[i[0]] = i[1]
        return out_dict
    
    # get nse index gainer
    def get_index_gainers(self) -> dict:
        url = self.nse_apis["nse_base_url"] + self.nse_apis["index_gainers"]
        # response = self.session.get(url, headers=self.nse_headers, timeout=5, cookies=self.cookies)
        response = self.nse_url_fetch(url=url)
        if response.status_code == 200:
            index_gainers = response.json()
            index_gainers_legends_unique = list()
            index_gainers_legends_details = dict()
            for i in index_gainers.get("legends"):
                index_gainers_legends_unique.append(i[0])
                index_gainers_legends_details[i[0]] = i[1]
            index_gainers_list_df = list()
            for i in index_gainers_legends_unique:
                # print(f"{i=}")
                # print(f'{len(index_loosers.get(i).get("data"))=}')
                if len(index_gainers.get(i).get("data")) == 0:
                    continue     
                df = (pd.DataFrame(index_gainers.get(i).get("data"))).loc[:, self.index_gainers_loosers_col]
                df.insert(loc=0, column="index_type", value="index - " + i)
                df.insert(loc=2, column="as_of_date", value=index_gainers.get(i).get("timestamp"))
                df.insert(loc=0, column="gain_loss", value="gain")
                index_gainers_list_df.append(df)
            index_gainers_df = pd.concat(index_gainers_list_df, axis=0)
            # print(f"size of gainers data: {index_gainers_df.shape}")
            # print(f"gain or loass: {index_gainers_df["gain_loss"].unique()}")
            
            index_gainers_df["frm_prevday_gapup%"] = round(((index_gainers_df["open_price"] - index_gainers_df["prev_price"]) / index_gainers_df["prev_price"]) * 100, 2)
            index_gainers_df["frm_prevday_gain%"] = round(((index_gainers_df["ltp"] - index_gainers_df["prev_price"]) / index_gainers_df["prev_price"]) * 100, 2)
        
            return index_gainers_df
        else:
            return {"error": "Failed to fetch data"}
    
    # get nse index looser
    def get_index_loosers(self) -> dict:
        url = self.nse_apis["nse_base_url"] + self.nse_apis["index_loosers"]
        # response = self.session.get(url, headers=self.nse_headers, timeout=5, cookies=self.cookies)
        response = self.nse_url_fetch(url=url)
        if response.status_code == 200:
            index_loosers = response.json()
            index_loosers_legends_unique = list()
            index_loosers_legends_details = dict()
            for i in index_loosers.get("legends"):
                index_loosers_legends_unique.append(i[0])
                index_loosers_legends_details[i[0]] = i[1]
            index_loosers_list_df = list()
            for i in index_loosers_legends_unique:
                # print(f"{i=}")
                # print(f'{len(index_loosers.get(i).get("data"))=}')
                if len(index_loosers.get(i).get("data")) == 0:
                    continue
                df = (pd.DataFrame(index_loosers.get(i).get("data"))).loc[:, self.index_gainers_loosers_col]
                df.insert(loc=0, column="index_type", value="index - " + i)
                df.insert(loc=2, column="as_of_date", value=index_loosers.get(i).get("timestamp"))
                df.insert(loc=0, column="gain_loss", value="loss")
                index_loosers_list_df.append(df)
            index_loosers_df = pd.concat(index_loosers_list_df, axis=0)
            # print(f"size of loosers data: {index_loosers_df.shape}")
            # print(f"gain or loass: {index_loosers_df["gain_loss"].unique()}")
            
            index_loosers_df["frm_prevday_gapup%"] = round(((index_loosers_df["open_price"] - index_loosers_df["prev_price"]) / index_loosers_df["prev_price"]) * 100, 2)
            index_loosers_df["frm_prevday_gain%"] = round(((index_loosers_df["ltp"] - index_loosers_df["prev_price"]) / index_loosers_df["prev_price"]) * 100, 2)
            return index_loosers_df
        else:
            return {"error": "Failed to fetch data"}
    
    # get nse fii dii data 
    def get_fii_dii_data(self) -> dict:
        url =  self.nse_apis["nse_base_url"] + self.nse_apis["nse_fii_dii"]
        response = self.session.get(url, headers=self.nse_headers, timeout=5, cookies=self.cookies)
        if response.status_code == 200:
            out = response.json()
            out_df = pd.DataFrame(out)
        return out_df

    def get_etfs(self):
        # session = requests.Session()
        # request = session.get(self.nse_apis["nse_base_url"], headers=self.nse_headers, timeout=10)
        # cookies = dict(request.cookies)
        # print(f"{cookies=}")
        # response = session.get(url, headers=self.nse_headers, timeout=50, cookies=cookies)
        
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        #     "Content-Type": "application/json; charset=utf-8",
        #     # "Access-Control-Allow-Origin": "nseindia.com",
        #     # "X-Content-Type-Options:": "nosniff",
        #     # "Strict-Transport-Security": "max-age=31536000 ; includeSubDomains ; preload",
        #     "Accept-Encoding": "gzip, deflate, br, zstd",
        #     "Accept-Language": "en-US,en;q=0.9",
        # }
        
        headers = {'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'www1.nseindia.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # cookies = dict("""_ga=GA1.1.568707584.1700285734; _ga_E0LYHCLJY3=GS1.1.1743171874.1.0.1743171914.0.0.0; _ga_WM2NSQKJEK=GS1.1.1743317888.17.1.1743317888.0.0.0; _ga_87M7PJ3R97=GS1.1.1743317888.17.1.1743317888.60.0.0; _abck=B44A8E6E8B8867E43E7B24A02C27F1AD~0~YAAQEQkgF9j9F6eVAQAAHPHX5Q00zp0gXrCxCaUA2d/m9XxNyXSaNEe3flx6CjjPHUK1I3UKGgzFIv/+osEyebyiIAoF6Nd35YqhR3MzxzqXeHKfMUWAOOMc3SAS3LMskjRwKVemud40oPJoLpnRM/hwxDlkwWHrAoZnOI9gnxSHRPfAAhhcgopYjQu2wsNR03t8DhxmstEeFth2Ms1TAIBRcN2rhIU9OeszA9vbvYTCfHEvI/tRoD6G6kQdqJBzdLozMs2DmuUPWUhkoaWhwBvcCErisjz12HGn/rG3G0bPQualeLWk9Nmz7vVW/1RhGPu8RBVmtHS0UXq+IezxFUKovpvQQ4/dCjiq8agHb3kNET/Xj4UGHpqoyaxmmSE4PLIyYPHCdjdhTT52cRrFfLowmNjJ3iFo5jPHm+oBaioKjNLLPC+34B7HvKIs+ATn0bzXfA4t7W5TgZxdM1J3CQ1lwPy0vshltFb46gY5Ij3JnDstpWI85CEoeFLDi3i89uY+oW6VI42RVEwJb/7ikgh4GQ==~-1~-1~-1; bm_sz=7A98BB7843A64087C596EA7EFE2A7FE1~YAAQEQkgF9n9F6eVAQAAHPHX5RusZ5txPNE4PaHOgSPrlkGvQHQZbBg5bo2rxyPK9M173fPjpMXpLg8HEFu5fjJJ5IEBhxwX2lyzOCmVsrJuVwrcJXyFhgURIFTGsnqE1bibvjB4drU8WzC+zfM0roSmcWUYWFTe9nKmNuPzhqc4dmuR98dyLSppCcolI30MDCk7hDadzhdhFjldjVecSGfxng5Dsbe+ZaomV3w1ihT4zTZWmPHbjDpdKfGG/ev3lufCpG7aIDBEEjji1bArL91mPncdbAykTrb3xKqgKtSa6obQn/E9SidzOwpm5+2QPWogMrYv6enEKrJz1MgTglDX7qdH6shPAe/54C2uBA==~3556149~3553593; ak_bmsc=ACDE2DFE9707064D55D732942D5178B0~000000000000000000000000000000~YAAQEQkgF939F6eVAQAA1vLX5RtCyJ6WWxGbG6geMLcTg1TyxrqEoSJ+lMtEoGts0PS/On/P0ke9co7bRttfi8WMUAmh7EURN50Sf+Ga0Pt94DexWv2IIX8F4d4z2eh36AEMGmwgZ2wIWiWWVD+0qvOj58mja91MW5//AHardX3DIF3dsIEkqY6vsBsWM/rHbYoOkqFKxdT6YqSohxUVxX4LQOD/oTzUm6oyfkRXDUKjuJwXr868UcTA7fd7irsdVQL/nn8c9L6Cfs4mgQhE+Es4lZiF30YGr9vu3zBTIBNFoKDikX8esgzDI+Ig9jOYkXMa7MU0aHIbf4z/84oIHzHADPlRNSOX2WLbhWignns2nm7P5svGSMHubjL3JT41oM3pVXT0SH+rno4J7A==; RT="z=1&dm=nseindia.com&si=546615dd-177d-43cb-83b7-1c83d7ebd749&ss=m8vagisl&sl=0&se=8c&tt=0&bcn=%2F%2F684d0d41.akstat.io%2F"; bm_sv=FD22F1E79AC54BC4892D2701BE2FDD19~YAAQDQkgFxUfNrGVAQAAmIH15RuKuxW0DHR5QzNwe4iGu3oCAIErGK/cYxGrmMb14KazTny679cVcG/J6+EBj62nSx+16scaMVG3HWfdESfCYeq3dtiNEM1iB+IP5HeWbkg6DbF3t6bPLe715yzZh0ts3zg4uYB0VeFJTx7Nctu7N2sf1FqAH6BRpNYx2lOVUDKxWlb/7triewicknQdXfC1Yl4l4zRWJcExnKFwvxCBYc6/nESlPjmF7jDcNa6F4Rmfog==~1""")

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Connection': 'keep-alive',
            # 'Host': 'www1.nseindia.com',
            'X-Requested-With': 'XMLHttpRequest',
            "Referer": "https://www.nseindia.com/",
        }
        # print(f"{cookies=}")
        # print(f"{self.cookies=}")
        
        # url = self.nse_apis["nse_base_url"] + self.nse_apis["nse_etf"]
        # url = "https://www.nseindia.com/api/etf"
        url = "https://www.nseindia.com/api/quote-equity?symbol=AXISVALUE"
        # response = self.session.get(url, headers=headers, cookies=self.cookies,timeout=5)
        try:
            response = self.session.get(url, headers=headers, cookies=self.cookies, timeout=300)
            print(f"{response.status_code=}")
            
            # elif response.status_code == 401:
            #     print(f"inside new code")
            #     new_session = requests.Session()
            #     new_request = new_session.get(self.nse_apis["nse_base_url"], headers=headers, timeout=1000)
            #     new_cookies = dict(new_request.cookies)
            #     new_response = new_session.get(url, headers=headers, cookies=new_cookies, timeout=1000)
            #     print(f"{new_response.status_code=}")
            #     out = new_response.json()
        except Exception as e:
            print(f"error: {e}, {response.status_code=}")                
        else:
            if response.status_code == 200:
                out = response.json()
                return out
        # if response.status_code == 200:
        #     out = response.json()
        #     return out
        # else:
        #     return {"error": "Api has some issue"}
            
        # response = self.session.get(url, headers=self.nse_headers, timeout=100, cookies=self.cookies)
        # print(f"{response=}")
        # print(response.status_code)
        # if response.status_code == 200:
        #     out = response.json()
        #     # out_df = pd.DataFrame(out.get("data"))
        #     return out
        # else:
        #     return {"error": "Api has some issue"}
    
    def nse_url_fetch(self, url, original_url="https://nseindia.com"):
        default_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        
        header = {
            "referer": "https://www.nseindia.com/",
             "Connection": "keep-alive",
             "Cache-Control": "max-age=0",
             "DNT": "1",
             "Upgrade-Insecure-Requests": "1",
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
             "Sec-Fetch-User": "?1",
             "Accept": "ext/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
             "Sec-Fetch-Site": "none",
             "Sec-Fetch-Mode": "navigate",
             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
        }
        
        nse_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Accept-Language': 'en,gu;q=0.9,hi;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'accept-encoding': 'gzip, deflate, br'
        }
        
        nse_session = requests.session()
        nse_request = nse_session.get(original_url, headers=default_header)
        nse_cookies = nse_request.cookies
        return nse_session.get(url, headers=default_header, cookies=nse_cookies)
        

def get_company_current_stock_price(company_symbol: str) -> dict:
    # https://www.nseindia.com/api/quote-equity?symbol=SANGHVIMOV
    return 1


if __name__ == "__main__":
    # company_list = ["SANGHVIMOV"]
    # for i in company_list:
    #     out = company_meta_details(i)
    #     print(out)
    
    nse = NSE()
    # out = nse.get_index_gainers()
    # out = nse.get_index_loosers()
    # out = nse.get_marketstate_daily()
    # out = nse.get_fii_dii_data()
    # out = nse.get_nifty50_daily_data()
    # out = nse.get_index_symbol()
    # out = nse.get_etfs()
    out = nse.nse_url_fetch(url="https://www.nseindia.com/api/quote-equity?symbol=AXISVALUE").json()
    print(f"{out}")
    