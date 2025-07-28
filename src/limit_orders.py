from .bot import BasicBot
from .validator import validate_positive_number, validate_symbol
import logging

class LimitOrders(BasicBot):
    def __init__(self):
        super().__init__()
        logging.info("LimitOrders initialized")

    def place_limit_buy_order(self, symbol, quantity, price):
        try:
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_positive_number(price, "price"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            # Place futures limit buy order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side='BUY',
                type='LIMIT',
                timeInForce='GTC',  # Good Till Cancelled
                quantity=quantity,
                price=str(price)  # Price must be string for futures API
            )
            
            logging.info(f"Futures limit buy order placed for {symbol.upper()} with quantity {quantity} at price {price}")
            logging.info(f"Order details: {order}")
            return order
    
        except Exception as e:
            logging.error(f"Error placing limit buy order: {e}")
            return None

    def place_limit_sell_order(self, symbol, quantity, price):
        try:
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_positive_number(price, "price"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            # Place futures limit sell order
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side='SELL',
                type='LIMIT',
                timeInForce='GTC',  # Good Till Cancelled
                quantity=quantity,
                price=str(price)  # Price must be string for futures API
            )
            
            logging.info(f"Futures limit sell order placed for {symbol.upper()} with quantity {quantity} at price {price}")
            logging.info(f"Order details: {order}")
            return order
        
        except Exception as e:
            logging.error(f"Error placing limit sell order: {e}")
            return None