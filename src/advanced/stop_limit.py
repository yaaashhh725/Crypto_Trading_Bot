from src.bot import BasicBot
from src.validator import validate_positive_number, validate_symbol
import logging

class StopLimitOrders(BasicBot):
    def __init__(self):
        super().__init__()
        logging.info("StopLimitOrders initialized for Futures trading")

    def place_stop_loss_order(self, symbol, quantity, stop_price, limit_price, side='SELL'):
        """
        Place a stop-loss order (stops losses by selling when price drops)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            quantity: Amount to trade
            stop_price: Price that triggers the order
            limit_price: Maximum/minimum price for the limit order after trigger
            side: 'SELL' for long positions, 'BUY' for short positions
        """
        try:
            # Validate inputs
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_positive_number(stop_price, "stop_price"):
                return None
            if not validate_positive_number(limit_price, "limit_price"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            # For SELL stop-loss: stop_price should be below current market price
            # For BUY stop-loss: stop_price should be above current market price
            
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='STOP',  # Stop-loss order type
                timeInForce='GTC',
                quantity=quantity,
                price=str(limit_price),  # Limit price after trigger
                stopPrice=str(stop_price)  # Trigger price
            )
            
            logging.info(f"Stop-loss order placed for {symbol.upper()}: {side} {quantity} at stop {stop_price}, limit {limit_price}")
            logging.info(f"Order details: {order}")
            return order
            
        except Exception as e:
            logging.error(f"Error placing stop-loss order: {e}")
            return None

    def place_take_profit_order(self, symbol, quantity, stop_price, limit_price, side='SELL'):
        """
        Place a take-profit order (locks in profits by selling when price rises)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            quantity: Amount to trade
            stop_price: Price that triggers the order
            limit_price: Maximum/minimum price for the limit order after trigger
            side: 'SELL' for long positions, 'BUY' for short positions
        """
        try:
            # Validate inputs
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_positive_number(stop_price, "stop_price"):
                return None
            if not validate_positive_number(limit_price, "limit_price"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='TAKE_PROFIT',  # Take-profit order type
                timeInForce='GTC',
                quantity=quantity,
                price=str(limit_price),  # Limit price after trigger
                stopPrice=str(stop_price)  # Trigger price
            )
            
            logging.info(f"Take-profit order placed for {symbol.upper()}: {side} {quantity} at stop {stop_price}, limit {limit_price}")
            logging.info(f"Order details: {order}")
            return order
            
        except Exception as e:
            logging.error(f"Error placing take-profit order: {e}")
            return None

    def place_stop_limit_bracket(self, symbol, quantity, entry_price, stop_loss_price, take_profit_price, side='BUY'):
        """
        Place a complete bracket order: entry + stop-loss + take-profit
        
        Args:
            symbol: Trading pair
            quantity: Amount to trade
            entry_price: Initial entry limit price
            stop_loss_price: Stop-loss trigger price
            take_profit_price: Take-profit trigger price
            side: 'BUY' for long, 'SELL' for short
        """
        orders = []
        
        try:
            # 1. Entry order (limit order)
            entry_order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=str(entry_price)
            )
            
            orders.append(('entry', entry_order))
            logging.info(f"Entry order placed: {entry_order}")
            
            # 2. Stop-loss order (opposite side)
            opposite_side = 'SELL' if side.upper() == 'BUY' else 'BUY'
            
            stop_loss_order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=opposite_side,
                type='STOP',
                timeInForce='GTC',
                quantity=quantity,
                price=str(stop_loss_price * 0.995 if opposite_side == 'SELL' else stop_loss_price * 1.005),  # Small buffer
                stopPrice=str(stop_loss_price)
            )
            
            orders.append(('stop_loss', stop_loss_order))
            logging.info(f"Stop-loss order placed: {stop_loss_order}")
            
            # 3. Take-profit order
            take_profit_order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=opposite_side,
                type='TAKE_PROFIT',
                timeInForce='GTC',
                quantity=quantity,
                price=str(take_profit_price),
                stopPrice=str(take_profit_price)
            )
            
            orders.append(('take_profit', take_profit_order))
            logging.info(f"Take-profit order placed: {take_profit_order}")
            
            return orders
            
        except Exception as e:
            logging.error(f"Error placing bracket orders: {e}")
            # Try to cancel any orders that were placed
            for order_type, order in orders:
                try:
                    self.client.futures_cancel_order(symbol=symbol.upper(), orderId=order['orderId'])
                    logging.info(f"Cancelled {order_type} order: {order['orderId']}")
                except:
                    pass
            return None

    def get_current_price(self, symbol):
        """Get current market price for reference"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            return float(ticker['price'])
        except Exception as e:
            logging.error(f"Error getting current price: {e}")
            return None
