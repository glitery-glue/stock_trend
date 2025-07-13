import sys
import pandas as pd
from src.logger import logging
from src.exception import CustomException

from src.sentiment_analysis import SentimentAnalysis
from src.text_cleaning import TextCleaner
from src.get_reddit_data import RedditData

class Predict:
    def __init__(self):
        self.reddit_data=RedditData()
        self.cleaner=TextCleaner()
        self.sentiment_analysis = SentimentAnalysis()
    def predict(self, stock_symbol, stock_type):
        logging.info ("started predicting")
        try:
            post_df = self.reddit_data.get_reddit_data(stock_symbol,stock_type)
            logging.info(" Reddit search is done")
            post_df['full_text']= post_df['full_text'].apply(self.cleaner.clean_text)
            post_df['full_text']= post_df['full_text'].apply(self.cleaner.text_processing)
            logging.info("cleaning is done")
            sentiment_result=self.sentiment_analysis.get_result(post_df, stock_symbol)
            logging.info("sentiment analysis is done")
            return sentiment_result
        except Exception as e:
            raise CustomException(e,sys)
