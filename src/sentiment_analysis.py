import sys
import nltk
import pandas as pd
from src.logger import logging
from src.exception import CustomException
from nltk.sentiment import SentimentIntensityAnalyzer


# Download required NLTK data
nltk.download('vader_lexicon')
class SentimentAnalysis:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.quality_threshold = 0.5  

    def quality_of_post(self, df):
        try:
            score = 0

            if len(df['text']) > 100:
                score += 0.3

            if df['score'] > 10:
                score += 0.3

            sentiment_scores = self.sia.polarity_scores(df['full_text'])
            score += abs(sentiment_scores['compound']) * 0.4
            return score
        except Exception as e:
            raise CustomException(e,sys)
    
    def filter_low_quality_posts(self, posts_df):
        try:
            posts_df['quality_score'] = posts_df.apply(self.quality_of_post, axis=1)
            return posts_df[posts_df['quality_score'] > self.quality_threshold]
        except Exception as e:
            raise CustomException(e,sys)
    def analyze_sentiment(self, text):
        try:
            vader_sentiment = self.sia.polarity_scores(text)
            
        
            text_length = len(text)
            has_question = 1 if '?' in text else 0
            has_exclamation = 1 if '!' in text else 0
            
    
            sentiment_score = (
                vader_sentiment['compound'] * 0.8 +  
                (min(text_length, 500)/ 1000) * 0.1 +  
                (has_question * -0.05) +  
                (has_exclamation * 0.05)  
            )
            
            return sentiment_score  
        
        except Exception as e:
            raise CustomException(e,sys)
    
    def analyze_trend(self, df, window_size=7):
        if len(df) == 0:
            return {
                'trend': 'Neutral',
                'moving_avg': pd.Series(),
                'current_sentiment': 0
            }
        df_copy = df.copy()  
        df_copy['date'] = pd.to_datetime(df_copy['created_utc'])
        df_copy.set_index('date', inplace=True)
        

        daily_sentiment = df_copy['sentiment'].resample('D').mean()
        
       
        moving_avg = daily_sentiment.rolling(window=window_size).mean()
        
    
        trend = 'Neutral'
        if len(moving_avg) > 0:
            if moving_avg.iloc[-1] > 0.2:
                trend = 'Bullish'
            elif moving_avg.iloc[-1] < -0.2:
                trend = 'Bearish'
        
        return {
            'trend': trend,
            'moving_avg': moving_avg,
            'current_sentiment': moving_avg.iloc[-1] if len(moving_avg) > 0 else 0
        } 
    def categorize_sentiment(self, sentiment_score):
        if sentiment_score>0.5:
          return "very positive"
        elif sentiment_score>0:
          return "poistive"
        elif sentiment_score<=-0.5:
          return "Very negetive"
        elif sentiment_score>-0.5:
          return "negetive"
        else:
          return "neutral"
          

    def get_result(self,df, stock_symbol):
        try:

            if len(df) == 0:
                return {
                    'success': False,
                    'error': f'No Reddit posts found for {stock_symbol}'
                }
            # get high quality post
            df_cleaned = self.filter_low_quality_posts(df)
            if len(df_cleaned)== 0:
                return{
                    'success': False,
                    'error': f'No High quality Reddit posts found for {stock_symbol}'
                }
            # get sentiment score
            df_cleaned['sentiment']=df_cleaned['full_text'].apply(self.analyze_sentiment)

            # Categorize sentiment
            df_cleaned['sentiment_category'] = df_cleaned['sentiment'].apply(self.categorize_sentiment)

            # Calculate metrics
            avg_sentiment = df_cleaned['sentiment'].mean()
            sentiment_count = df_cleaned['sentiment_category'].value_counts().to_dict()

            
            # Get top posts
            top_posts = df_cleaned.nlargest(5, 'score')[['title', 'score', 'sentiment', 'subreddit','url']].to_dict('records')

            # Analyze trend
            sentiment_analyze = self.analyze_trend(df_cleaned)
            return {
                'Success': True,
                'stock_symbol': stock_symbol,
                'Sentiment':avg_sentiment,
                'Tendency': sentiment_count,
                'post count': len(df),
                'Top Post': top_posts,
                'Trend': sentiment_analyze,
            }
        except Exception as e:
            raise CustomException(e,sys)
