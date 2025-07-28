from binance import Client
from dotenv import load_dotenv 
import os
import logging

load_dotenv()

API_KEY = os.getenv("API_Key")
API_SECRET = os.getenv("Secret_Key")

class BasicBot:
    def __init__(self):
        if not API_KEY or not API_SECRET:
            logging.error("API_KEY or API_SECRET not found. Make sure to set them in your .env file.")
            raise ValueError("API credentials are not set in the environment variables.")
            
        self.client = Client(API_KEY, API_SECRET,testnet=True)

        self.client.API_URL = 'https://testnet.binancefuture.com'
        
        logging.info("Initialized Binance client")

    def get_account_info(self):
        """Get futures account information"""
        try:
            account_info = self.client.futures_account()
            logging.info("Successfully retrieved futures account information")
            return account_info
        except Exception as e:
            logging.error(f"Error retrieving account info: {e}")
            return None
        
    def get_current_price(self, symbol):
        """Get current market price for a symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            logging.info(f"Current price for {symbol.upper()}: {ticker['price']}")
            return float(ticker['price'])
        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {e}")
            return None
