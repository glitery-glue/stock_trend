import os
import sys
import time
import pandas as pd
import praw
import yfinance as yf
from datetime import datetime
from src.logger import logging
from src.exception import CustomException
from dotenv import load_dotenv
from requests.exceptions import HTTPError


load_dotenv()


class RedditData:
    def __init__(self):
        self.reddit = praw.Reddit(
                     client_id=os.getenv("REDDIT_CLIENT_ID"),
                     client_secret=os.getenv("REDDIT_SECRET_ID"),
                     user_agent=os.getenv("REDDIT_USER_AGENT"))
        
    
    def get_reddit_data(self, stock_symbol:str, stock_type:str,limit=100,max_try=3):
        logging.info("creating search query to search reddit")
        try:
            if stock_type=="India":
                subreddit="IndianStockMarket+IndianStreetBets+IndiaInvestments"
            else:
                subreddit='stocks+investing+wallstreetbets'
            data=[]
            result=self.reddit.subreddit(subreddit).search(f'{stock_symbol} stock',limit=limit,sort='new')
            logging.info("reddit search is done")
            for post in result:
                
                    full_text=f"{post.title} {post.selftext}"
                    data.append({
                        'stock_symbol': stock_symbol,
                        'title':post.title,
                        'text':post.selftext,
                        'score': post.score,
                        'full_text': full_text,
                        'created_utc': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'url': f'https://reddit.com{post.permalink}',
                        'subreddit': post.subreddit.display_name
                    })
            data=pd.DataFrame(data)
            logging.info("reddit search result is done")
            return data
            
        except Exception as e:
            raise CustomException(e,sys)


class YfData:
    def __init__(self):
        pass
    def get_yf_data(self, stock_symbol, max_retries=5, retry_delay=5):
        logging.info("get yf data")
        for attempt in range (max_retries):
            try:
                if attempt > 0:
                    time.sleep(retry_delay)
                stock = yf.Ticker(stock_symbol)
                try:
                    current_price = stock.info.get('currentPrice')
                    if current_price is None:
                        raise ValueError ("No current price is found")
                    return {
                        'stock_data':
                        {
                          'current price': current_price,
                          'currency': stock.info.get('currency', 'INR')
                        }
                    }
                except HTTPError as e:
                    if e.response.status_code == 429:
                        print(f"Rate limit hit, attempt {attempt + 1} of {max_retries}")
                        if attempt == max_retries - 1:
                            raise ValueError("Rate limit exceeded. Please try again later.")
                        continue
                    raise
                
            except Exception as e:
                print(f"Error fetching stock data (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': f"Failed to fetch stock data for {stock_symbol} after {max_retries} attempts: {str(e)}"
                    }
                continue 

                

if __name__=="__main__":
    stock_type='India'
    stock_name='RCF'
    reddit_data=RedditData()
    result = reddit_data.get_reddit_data(stock_name,stock_type)
    if result is not None and not result.empty:
        result.to_csv('rcf.csv', index=False)
        print("Saved to rcf.csv")
    else:
        print("No data fetched.")