import sys
from flask import Flask, render_template, request, jsonify
from src.predict import Predict
from src.get_reddit_data import YfData
from src.logger import logging
from src.exception import CustomException

app = Flask(__name__)

# Initialize analyzers
sentiment_result = Predict()
stock_data = YfData()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        stock_symbol = request.form.get('stock_symbol', '').upper()
        stock_type = request.form.get('stock_type', ' ').lower()
        logging.info("getting user data")
        sentiment_result = sentiment_result.predict(stock_symbol, stock_type)
        stock_data = stock_data.get_yf_data(stock_symbol)
        result = {
            'stock_symbol': stock_symbol,
            'sentiment': sentiment_result,
            'stock_data': stock_data
        }
        logging.info("done and dusted")
        return jsonify (result)
    except Exception as e :
        raise CustomException (e, sys)
    
if __name__ == '__main__':
    app.run(debug=True) 