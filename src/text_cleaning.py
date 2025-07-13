import sys
import re
import pandas as pd
from src.logger import logging
from src.exception import CustomException
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
class TextCleaner:
    def __init__(self):
        logging.info("data cleaning")
        self.stop_words = set(stopwords.words('english'))
        self.wl = WordNetLemmatizer()
    def clean_text(self, text):
        try:
            if not isinstance(text, str):
                return ""
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            # Remove Reddit-style links
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            # Remove special characters and digits
            text = re.sub(r'[^\w\s]', '', text)
            # lowecase
            text = text.lower()

            return text.strip()
        except Exception as e:
            raise CustomException(e,sys)
    def text_processing(self,text):
        try:
            tokens = word_tokenize(text)
            tokens= [word for word in tokens if word not in self.stop_words]
            tokens= [self.wl.lemmatize(word) for word in tokens] 

            return ' '.join(tokens)
        except Exception as e:
            raise CustomException(e,sys)