from src.bot import BasicBot
from src.validator import validate_positive_number, validate_symbol
import logging
import time

class OCOOrders(BasicBot):
    def __init__(self):
        super().__init__()
        logging.info("OCOOrders initialized for Futures trading")
        self.active_oco_orders = {}  # Track OCO order pairs

    def place_oco_order(self, symbol, quantity, take_profit_price, stop_loss_price, side='SELL'):
        """
        Place OCO (One-Cancels-Other) order: Take-profit + Stop-loss
        When one executes, the other is automatically cancelled
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            quantity: Amount to trade
            take_profit_price: Price for take-profit order
            stop_loss_price: Price for stop-loss order
            side: 'SELL' for closing long position, 'BUY' for closing short position
        """
        try:
            # Validate inputs
            if not validate_positive_number(quantity, "quantity"):
                return None
            if not validate_positive_number(take_profit_price, "take_profit_price"):
                return None
            if not validate_positive_number(stop_loss_price, "stop_loss_price"):
                return None
            if not validate_symbol(self.client, symbol):
                return None

            # Validate price logic
            current_price = self.get_current_price(symbol)
            if current_price:
                if side.upper() == 'SELL':
                    if take_profit_price <= current_price:
                        logging.error("Take-profit price should be above current price for SELL side")
                        return None
                    if stop_loss_price >= current_price:
                        logging.error("Stop-loss price should be below current price for SELL side")
                        return None
                else:  # BUY side
                    if take_profit_price >= current_price:
                        logging.error("Take-profit price should be below current price for BUY side")
                        return None
                    if stop_loss_price <= current_price:
                        logging.error("Stop-loss price should be above current price for BUY side")
                        return None

            # Place take-profit order
            take_profit_order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='TAKE_PROFIT',
                timeInForce='GTC',
                quantity=quantity,
                price=str(take_profit_price),
                stopPrice=str(take_profit_price)
            )
            
            logging.info(f"Take-profit order placed: {take_profit_order}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
            # Place stop-loss order
            stop_loss_order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='STOP',
                timeInForce='GTC',
                quantity=quantity,
                price=str(stop_loss_price * 0.995 if side.upper() == 'SELL' else stop_loss_price * 1.005),
                stopPrice=str(stop_loss_price)
            )
            
            logging.info(f"Stop-loss order placed: {stop_loss_order}")
            
            # Store OCO pair for monitoring
            oco_id = f"OCO_{int(time.time())}"
            self.active_oco_orders[oco_id] = {
                'symbol': symbol.upper(),
                'take_profit_order_id': take_profit_order['orderId'],
                'stop_loss_order_id': stop_loss_order['orderId'],
                'quantity': quantity,
                'side': side.upper(),
                'created_time': time.time()
            }
            
            oco_result = {
                'oco_id': oco_id,
                'symbol': symbol.upper(),
                'take_profit_order': take_profit_order,
                'stop_loss_order': stop_loss_order,
                'quantity': quantity,
                'side': side.upper()
            }
            
            logging.info(f"OCO orders created successfully: {oco_id}")
            return oco_result
            
        except Exception as e:
            logging.error(f"Error placing OCO order: {e}")
            return None

    def check_and_cancel_oco(self, oco_id):
        """
        Check if one order from OCO pair is filled and cancel the other
        
        Args:
            oco_id: The OCO identifier
        """
        try:
            if oco_id not in self.active_oco_orders:
                logging.warning(f"OCO ID {oco_id} not found in active orders")
                return None
                
            oco_data = self.active_oco_orders[oco_id]
            symbol = oco_data['symbol']
            tp_order_id = oco_data['take_profit_order_id']
            sl_order_id = oco_data['stop_loss_order_id']
            
            # Check status of both orders
            tp_order = self.client.futures_get_order(symbol=symbol, orderId=tp_order_id)
            sl_order = self.client.futures_get_order(symbol=symbol, orderId=sl_order_id)
            
            # If take-profit is filled, cancel stop-loss
            if tp_order['status'] == 'FILLED':
                try:
                    cancel_result = self.client.futures_cancel_order(symbol=symbol, orderId=sl_order_id)
                    logging.info(f"Take-profit filled, cancelled stop-loss order: {cancel_result}")
                    del self.active_oco_orders[oco_id]
                    return {'filled': 'take_profit', 'cancelled': 'stop_loss', 'filled_order': tp_order}
                except Exception as e:
                    logging.warning(f"Could not cancel stop-loss order (might be already filled): {e}")
            
            # If stop-loss is filled, cancel take-profit
            elif sl_order['status'] == 'FILLED':
                try:
                    cancel_result = self.client.futures_cancel_order(symbol=symbol, orderId=tp_order_id)
                    logging.info(f"Stop-loss filled, cancelled take-profit order: {cancel_result}")
                    del self.active_oco_orders[oco_id]
                    return {'filled': 'stop_loss', 'cancelled': 'take_profit', 'filled_order': sl_order}
                except Exception as e:
                    logging.warning(f"Could not cancel take-profit order (might be already filled): {e}")
            
            return {'status': 'both_active', 'tp_status': tp_order['status'], 'sl_status': sl_order['status']}
            
        except Exception as e:
            logging.error(f"Error checking OCO status: {e}")
            return None

    def cancel_oco_orders(self, oco_id):
        """Cancel both orders in an OCO pair"""
        try:
            if oco_id not in self.active_oco_orders:
                logging.warning(f"OCO ID {oco_id} not found")
                return None
                
            oco_data = self.active_oco_orders[oco_id]
            symbol = oco_data['symbol']
            
            results = []
            
            # Cancel take-profit order
            try:
                tp_cancel = self.client.futures_cancel_order(
                    symbol=symbol, 
                    orderId=oco_data['take_profit_order_id']
                )
                results.append(('take_profit', tp_cancel))
                logging.info(f"Cancelled take-profit order: {tp_cancel}")
            except Exception as e:
                logging.warning(f"Could not cancel take-profit order: {e}")
                
            # Cancel stop-loss order
            try:
                sl_cancel = self.client.futures_cancel_order(
                    symbol=symbol, 
                    orderId=oco_data['stop_loss_order_id']
                )
                results.append(('stop_loss', sl_cancel))
                logging.info(f"Cancelled stop-loss order: {sl_cancel}")
            except Exception as e:
                logging.warning(f"Could not cancel stop-loss order: {e}")
            
            # Remove from active tracking
            del self.active_oco_orders[oco_id]
            
            return results
            
        except Exception as e:
            logging.error(f"Error cancelling OCO orders: {e}")
            return None

    def get_active_oco_orders(self):
        """Get all active OCO order pairs"""
        return self.active_oco_orders.copy()

    def get_current_price(self, symbol):
        """Get current market price for reference"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            return float(ticker['price'])
        except Exception as e:
            logging.error(f"Error getting current price: {e}")
            return None
            
