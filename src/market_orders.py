from .bot import BasicBot
from .validator import validate_positive_number, validate_symbol
import logging

class MarketOrders(BasicBot):
    def __init__(self):
        super().__init__()
        logging.info("MarketOrders initialized")

    def place_buy_order(self, symbol, quantity):
        try:
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            # Place futures market buy order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            # order = self.client.order_market_buy(
            #     symbol=symbol.upper(),
            #     quantity=quantity
            # )
            
            logging.info(f"Futures market buy order placed for {symbol.upper()} with quantity {quantity}")
            logging.info(f"Order details: {order}")
            return order
        except Exception as e:
            logging.error(f"Error placing buy order: {e}")
            return None

    def place_sell_order(self, symbol, quantity):
        try:
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            # Place futures market sell order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            
            logging.info(f"Futures market sell order placed for {symbol.upper()} with quantity {quantity}")
            logging.info(f"Order details: {order}")
            return order
        
        except Exception as e:
            logging.error(f"Error placing sell order: {e}")
            return None
    
    def get_market_price(self, symbol):
        """Get current market price for a symbol"""
        try:
            if not validate_symbol(self.client, symbol):
                return None
            # Fetch current market price
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            price = float(ticker['price'])
            logging.info(f"Current market price for {symbol.upper()}: {price}")
            return price
        except Exception as e:
            logging.error(f"Error getting market price for {symbol}: {e}")
            return None
