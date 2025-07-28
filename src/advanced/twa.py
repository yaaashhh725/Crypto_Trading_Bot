from src.bot import BasicBot
from src.validator import validate_positive_number, validate_symbol
import logging
import time
import threading
from datetime import datetime

class TWAPOrders(BasicBot):
    def __init__(self):
        super().__init__()
        logging.info("TWAPOrders initialized for Futures trading")
        self.active_twap_orders = {}  # Track active TWAP executions

    def place_twap_order(self, symbol, total_quantity, side, duration_minutes, num_chunks=None, order_type='MARKET'):
        """
        Place TWAP (Time-Weighted Average Price) order
        Splits large order into smaller chunks executed over time
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            total_quantity: Total amount to trade
            side: 'BUY' or 'SELL'
            duration_minutes: Time period to spread the order over
            num_chunks: Number of smaller orders (default: duration_minutes)
            order_type: 'MARKET' or 'LIMIT'
        """
        try:
            # Validate inputs
            if not validate_positive_number(total_quantity, "total_quantity"):
                return None
            if not validate_positive_number(duration_minutes, "duration_minutes"):
                return None
            if not validate_symbol(self.client, symbol):
                return None
            
            if side.upper() not in ['BUY', 'SELL']:
                logging.error("Side must be 'BUY' or 'SELL'")
                return None
                
            # Default chunks to duration in minutes (1 chunk per minute)
            if num_chunks is None:
                num_chunks = max(1, int(duration_minutes))
            
            # Calculate chunk parameters
            chunk_size = total_quantity / num_chunks
            interval_seconds = (duration_minutes * 60) / num_chunks
            
            # Minimum chunk size check (exchange specific)
            min_chunk_size = self.get_min_quantity(symbol)
            if min_chunk_size and chunk_size < min_chunk_size:
                logging.error(f"Chunk size {chunk_size} is below minimum {min_chunk_size}")
                return None
            
            twap_id = f"TWAP_{int(time.time())}"
            
            twap_config = {
                'twap_id': twap_id,
                'symbol': symbol.upper(),
                'total_quantity': total_quantity,
                'side': side.upper(),
                'order_type': order_type.upper(),
                'duration_minutes': duration_minutes,
                'num_chunks': num_chunks,
                'chunk_size': chunk_size,
                'interval_seconds': interval_seconds,
                'chunks_executed': 0,
                'total_executed': 0,
                'start_time': datetime.now(),
                'status': 'ACTIVE',
                'executed_orders': [],
                'errors': []
            }
            
            self.active_twap_orders[twap_id] = twap_config
            
            logging.info(f"TWAP order initiated: {twap_id}")
            logging.info(f"Total: {total_quantity}, Chunks: {num_chunks}, Size: {chunk_size}, Interval: {interval_seconds}s")
            
            # Start execution in separate thread
            execution_thread = threading.Thread(
                target=self._execute_twap_chunks,
                args=(twap_id,),
                daemon=True
            )
            execution_thread.start()
            
            return twap_config
            
        except Exception as e:
            logging.error(f"Error initiating TWAP order: {e}")
            return None

    def _execute_twap_chunks(self, twap_id):
        """Execute TWAP chunks in background thread"""
        try:
            twap_config = self.active_twap_orders[twap_id]
            symbol = twap_config['symbol']
            side = twap_config['side']
            chunk_size = twap_config['chunk_size']
            num_chunks = twap_config['num_chunks']
            interval_seconds = twap_config['interval_seconds']
            order_type = twap_config['order_type']
            
            for chunk_num in range(num_chunks):
                try:
                    # Check if TWAP was cancelled
                    if twap_config.get('status') == 'CANCELLED':
                        logging.info(f"TWAP {twap_id} cancelled, stopping execution")
                        break
                    
                    # Adjust last chunk size for any remainder
                    current_chunk_size = chunk_size
                    if chunk_num == num_chunks - 1:
                        remaining = twap_config['total_quantity'] - twap_config['total_executed']
                        current_chunk_size = remaining
                    
                    # Execute chunk order
                    if order_type == 'MARKET':
                        order = self._place_market_chunk(symbol, current_chunk_size, side)
                    else:  # LIMIT
                        current_price = self.get_current_price(symbol)
                        if not current_price:
                            raise Exception("Could not get current price for limit order")
                        
                        # Small price adjustment for limit orders
                        if side == 'BUY':
                            limit_price = current_price * 1.001  # Slightly above market
                        else:
                            limit_price = current_price * 0.999  # Slightly below market
                            
                        order = self._place_limit_chunk(symbol, current_chunk_size, side, limit_price)
                    
                    if order:
                        twap_config['chunks_executed'] += 1
                        twap_config['total_executed'] += float(order.get('executedQty', current_chunk_size))
                        twap_config['executed_orders'].append(order)
                        
                        logging.info(f"TWAP {twap_id} - Chunk {chunk_num + 1}/{num_chunks} executed: {order.get('orderId')}")
                    else:
                        error_msg = f"Chunk {chunk_num + 1} failed to execute"
                        twap_config['errors'].append(error_msg)
                        logging.error(f"TWAP {twap_id} - {error_msg}")
                    
                    # Wait for next chunk (except for last chunk)
                    if chunk_num < num_chunks - 1:
                        time.sleep(interval_seconds)
                        
                except Exception as e:
                    error_msg = f"Error executing chunk {chunk_num + 1}: {str(e)}"
                    twap_config['errors'].append(error_msg)
                    logging.error(f"TWAP {twap_id} - {error_msg}")
                    continue
            
            # Mark as completed
            twap_config['status'] = 'COMPLETED'
            twap_config['end_time'] = datetime.now()
            
            logging.info(f"TWAP {twap_id} completed: {twap_config['chunks_executed']}/{num_chunks} chunks executed")
            
        except Exception as e:
            logging.error(f"Critical error in TWAP execution {twap_id}: {e}")
            if twap_id in self.active_twap_orders:
                self.active_twap_orders[twap_id]['status'] = 'ERROR'
                self.active_twap_orders[twap_id]['errors'].append(str(e))

    def _place_market_chunk(self, symbol, quantity, side):
        """Place a market order chunk"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            return order
        except Exception as e:
            logging.error(f"Error placing market chunk: {e}")
            return None

    def _place_limit_chunk(self, symbol, quantity, side, price):
        """Place a limit order chunk"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=str(price)
            )
            return order
        except Exception as e:
            logging.error(f"Error placing limit chunk: {e}")
            return None

    def get_twap_status(self, twap_id):
        """Get status of a TWAP order"""
        if twap_id not in self.active_twap_orders:
            return None
        return self.active_twap_orders[twap_id].copy()

    def cancel_twap_order(self, twap_id):
        """Cancel an active TWAP order"""
        try:
            if twap_id not in self.active_twap_orders:
                logging.warning(f"TWAP ID {twap_id} not found")
                return False
            
            self.active_twap_orders[twap_id]['status'] = 'CANCELLED'
            logging.info(f"TWAP {twap_id} marked for cancellation")
            return True
            
        except Exception as e:
            logging.error(f"Error cancelling TWAP order: {e}")
            return False

    def get_active_twap_orders(self):
        """Get all active TWAP orders"""
        return {k: v for k, v in self.active_twap_orders.items() if v['status'] == 'ACTIVE'}

    def get_min_quantity(self, symbol):
        """Get minimum quantity for a symbol"""
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol.upper():
                    for filter_info in s['filters']:
                        if filter_info['filterType'] == 'LOT_SIZE':
                            return float(filter_info['minQty'])
            return None
        except Exception as e:
            logging.error(f"Error getting minimum quantity: {e}")
            return None

    def get_current_price(self, symbol):
        """Get current market price"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            return float(ticker['price'])
        except Exception as e:
            logging.error(f"Error getting current price: {e}")
            return None