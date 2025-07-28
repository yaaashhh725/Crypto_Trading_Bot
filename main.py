from src.market_orders import MarketOrders
from src.limit_orders import LimitOrders
from src.advanced.oco import OCOOrders
from src.advanced.stop_limit import StopLimitOrders
from src.advanced.twa import TWAPOrders
import logging
import argparse


def setup_logging():
    """Sets up the logging configuration to output to a file."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='bot.log',
        filemode='a'  # Append to the log file
    )
    # Also, add a handler to print to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def display_order_details(order):
    """Display order details in a formatted way"""
    if not order:
        print(" Order placement failed. Check bot.log for details.")
        return
        
    print("\n" + "="*50)
    print("✅ ORDER PLACED SUCCESSFULLY")
    print("="*50)
    print(f"Symbol:          {order.get('symbol', 'N/A')}")
    print(f"Order ID:        {order.get('orderId', 'N/A')}")
    print(f"Client Order ID: {order.get('clientOrderId', 'N/A')}")
    print(f"Status:          {order.get('status', 'N/A')}")
    print(f"Side:            {order.get('side', 'N/A')}")
    print(f"Type:            {order.get('type', 'N/A')}")
    print(f"Quantity:        {order.get('origQty', 'N/A')}")
    
    if order.get('price'):
        print(f"Price:           {order.get('price', 'N/A')}")
    if order.get('stopPrice'):
        print(f"Stop Price:      {order.get('stopPrice', 'N/A')}")
    if order.get('avgPrice') and float(order.get('avgPrice', 0)) > 0:
        print(f"Average Price:   {order.get('avgPrice', 'N/A')}")
    if order.get('executedQty'):
        print(f"Executed Qty:    {order.get('executedQty', 'N/A')}")
    
    print(f"Time in Force:   {order.get('timeInForce', 'N/A')}")
    print(f"Update Time:     {order.get('updateTime', 'N/A')}")
    print("="*50)

def display_oco_details(oco_result):
    """Display OCO order details"""
    if not oco_result:
        print(" OCO order placement failed. Check bot.log for details.")
        return
        
    print("\n" + "="*60)
    print("✅ OCO ORDERS PLACED SUCCESSFULLY")
    print("="*60)
    print(f"OCO ID:          {oco_result['oco_id']}")
    print(f"Symbol:          {oco_result['symbol']}")
    print(f"Side:            {oco_result['side']}")
    print(f"Quantity:        {oco_result['quantity']}")
    
    print("\n TAKE-PROFIT ORDER:")
    tp_order = oco_result['take_profit_order']
    print(f"  Order ID:      {tp_order.get('orderId')}")
    print(f"  Price:         {tp_order.get('stopPrice')}")
    print(f"  Status:        {tp_order.get('status')}")
    
    print("\n STOP-LOSS ORDER:")
    sl_order = oco_result['stop_loss_order']
    print(f"  Order ID:      {sl_order.get('orderId')}")
    print(f"  Price:         {sl_order.get('stopPrice')}")
    print(f"  Status:        {sl_order.get('status')}")
    
    print("="*60)

def display_twap_details(twap_config):
    """Display TWAP order details"""
    if not twap_config:
        print(" TWAP order placement failed. Check bot.log for details.")
        return
        
    print("\n" + "="*60)
    print("✅ TWAP ORDER INITIATED SUCCESSFULLY")
    print("="*60)
    print(f"TWAP ID:         {twap_config['twap_id']}")
    print(f"Symbol:          {twap_config['symbol']}")
    print(f"Side:            {twap_config['side']}")
    print(f"Total Quantity:  {twap_config['total_quantity']}")
    print(f"Duration:        {twap_config['duration_minutes']} minutes")
    print(f"Number of Chunks: {twap_config['num_chunks']}")
    print(f"Chunk Size:      {twap_config['chunk_size']}")
    print(f"Interval:        {twap_config['interval_seconds']:.1f} seconds")
    print(f"Order Type:      {twap_config['order_type']}")
    print(f"Status:          {twap_config['status']}")
    print("="*60)
    print(" TWAP execution started in background...")

def display_grid_details(grid_config):
    """Display Grid strategy details"""
    if not grid_config:
        print(" Grid strategy creation failed. Check bot.log for details.")
        return
        
    print("\n" + "="*60)
    print("✅ GRID STRATEGY CREATED SUCCESSFULLY")
    print("="*60)
    print(f"Grid ID:         {grid_config['grid_id']}")
    print(f"Symbol:          {grid_config['symbol']}")
    print(f"Price Range:     ${grid_config['lower_price']:,.2f} - ${grid_config['upper_price']:,.2f}")
    print(f"Current Price:   ${grid_config['current_price']:,.2f}")
    print(f"Grid Levels:     {grid_config['num_grids']}")
    print(f"Total Quantity:  {grid_config['total_quantity']}")
    print(f"Grid Type:       {grid_config['grid_type']}")
    print(f"Buy Orders:      {len(grid_config['buy_orders'])}")
    print(f"Sell Orders:     {len(grid_config['sell_orders'])}")
    print(f"Status:          {grid_config['status']}")
    print("="*60)

def main():
    """Main function to parse arguments and execute trading bot actions."""
    parser = argparse.ArgumentParser(
        description="PrimeTrade.ai Binance Futures Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic Orders:
    python main.py market --symbol BTCUSDT --side buy --quantity 0.001
    python main.py limit --symbol BTCUSDT --side buy --quantity 0.001 --price 30000
    
  Advanced Orders:
    python main.py stop-loss --symbol BTCUSDT --quantity 0.001 --stop-price 29000 --limit-price 28900
    python main.py take-profit --symbol BTCUSDT --quantity 0.001 --stop-price 31000 --limit-price 31100
    python main.py oco --symbol BTCUSDT --quantity 0.001 --take-profit 31000 --stop-loss 29000
    python main.py twap --symbol BTCUSDT --side buy --total-quantity 0.01 --duration 10 --chunks 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='order_type', help='The type of order to place', required=True)

    # --- Market Order Parser ---
    market_parser = subparsers.add_parser('market', help='Place a market order')
    market_parser.add_argument('--symbol', type=str, required=True, 
                              help='The trading symbol (e.g., BTCUSDT, ETHUSDT)')
    market_parser.add_argument('--side', type=str, required=True, choices=['buy', 'sell'], 
                              help='The order side: buy or sell')
    market_parser.add_argument('--quantity', type=float, required=True, 
                              help='The quantity to trade (must be positive)')

    # --- Limit Order Parser ---
    limit_parser = subparsers.add_parser('limit', help='Place a limit order')
    limit_parser.add_argument('--symbol', type=str, required=True, 
                             help='The trading symbol (e.g., BTCUSDT, ETHUSDT)')
    limit_parser.add_argument('--side', type=str, required=True, choices=['buy', 'sell'], 
                             help='The order side: buy or sell')
    limit_parser.add_argument('--quantity', type=float, required=True, 
                             help='The quantity to trade (must be positive)')
    limit_parser.add_argument('--price', type=float, required=True, 
                             help='The price for the limit order (must be positive)')

    # --- Stop-Loss Order Parser ---
    stop_loss_parser = subparsers.add_parser('stop-loss', help='Place a stop-loss order')
    stop_loss_parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    stop_loss_parser.add_argument('--quantity', type=float, required=True, help='Quantity to trade')
    stop_loss_parser.add_argument('--stop-price', type=float, required=True, help='Stop trigger price')
    stop_loss_parser.add_argument('--limit-price', type=float, required=True, help='Limit price after trigger')
    stop_loss_parser.add_argument('--side', type=str, default='sell', choices=['buy', 'sell'], help='Order side (default: sell)')

    # --- Take-Profit Order Parser ---
    take_profit_parser = subparsers.add_parser('take-profit', help='Place a take-profit order')
    take_profit_parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    take_profit_parser.add_argument('--quantity', type=float, required=True, help='Quantity to trade')
    take_profit_parser.add_argument('--stop-price', type=float, required=True, help='Stop trigger price')
    take_profit_parser.add_argument('--limit-price', type=float, required=True, help='Limit price after trigger')
    take_profit_parser.add_argument('--side', type=str, default='sell', choices=['buy', 'sell'], help='Order side (default: sell)')

    # --- OCO Order Parser ---
    oco_parser = subparsers.add_parser('oco', help='Place OCO (One-Cancels-Other) orders')
    oco_parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    oco_parser.add_argument('--quantity', type=float, required=True, help='Quantity to trade')
    oco_parser.add_argument('--take-profit', type=float, required=True, help='Take-profit price')
    oco_parser.add_argument('--stop-loss', type=float, required=True, help='Stop-loss price')
    oco_parser.add_argument('--side', type=str, default='sell', choices=['buy', 'sell'], help='Order side (default: sell)')

    # --- TWAP Order Parser ---
    twap_parser = subparsers.add_parser('twap', help='Place TWAP (Time-Weighted Average Price) order')
    twap_parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    twap_parser.add_argument('--side', type=str, required=True, choices=['buy', 'sell'], help='Order side')
    twap_parser.add_argument('--total-quantity', type=float, required=True, help='Total quantity to trade')
    twap_parser.add_argument('--duration', type=int, required=True, help='Duration in minutes')
    twap_parser.add_argument('--chunks', type=int, help='Number of chunks (default: duration)')
    twap_parser.add_argument('--order-type', type=str, default='market', choices=['market', 'limit'], help='Order type for chunks')

    args = parser.parse_args()

    logging.info(f"CLI arguments received: {args}")
    logging.info(f"Starting {args.order_type} order execution")

    try:
        if args.order_type == 'market':
            print(f"   Placing MARKET {args.side.upper()} order...")
            print(f"   Symbol: {args.symbol.upper()}")
            print(f"   Quantity: {args.quantity}")
            
            market_orders = MarketOrders()
            # print(market_orders.get_account_info())  # Fetch account info for context
            # Show current market price for reference
            # current_price = market_orders.get_market_price(args.symbol)
            # if current_price:
            #     print(f"   Current Price: ${current_price:,.2f}")
            #     estimated_value = current_price * args.quantity
            #     print(f"   Estimated Value: ${estimated_value:,.2f}")
            
            if args.side == 'buy':
                order = market_orders.place_buy_order(args.symbol, args.quantity)
            else:  # side == 'sell'
                order = market_orders.place_sell_order(args.symbol, args.quantity)

            display_order_details(order)

        elif args.order_type == 'limit':
            print(f" Placing LIMIT {args.side.upper()} order...")
            print(f"   Symbol: {args.symbol.upper()}")
            print(f"   Quantity: {args.quantity}")
            print(f"   Price: ${args.price:,.2f}")
            
            estimated_value = args.price * args.quantity
            print(f"   Total Value: ${estimated_value:,.2f}")
            
            limit_orders = LimitOrders()
            
            # Show current market price for comparison
            # current_price = limit_orders.get_market_price(args.symbol)
            # if current_price:
            #     price_diff = ((args.price - current_price) / current_price) * 100
            #     print(f"   Current Price: ${current_price:,.2f}")
            #     print(f"   Price Difference: {price_diff:+.2f}%")
            
            if args.side == 'buy':
                order = limit_orders.place_limit_buy_order(args.symbol, args.quantity, args.price)
            else:  # side == 'sell'
                order = limit_orders.place_limit_sell_order(args.symbol, args.quantity, args.price)
        
        # Display results
            display_order_details(order)
        
        elif args.order_type == 'stop-loss':
            print(f" Placing STOP-LOSS order...")
            print(f"   Symbol: {args.symbol.upper()}")
            print(f"   Side: {args.side.upper()}")
            print(f"   Quantity: {args.quantity}")
            print(f"   Stop Price: ${args.stop_price:,.2f}")
            print(f"   Limit Price: ${args.limit_price:,.2f}")
            
            stop_limit_orders = StopLimitOrders()
            
            # Show current market price for reference
            current_price = stop_limit_orders.get_current_price(args.symbol)
            if current_price:
                print(f"   Current Price: ${current_price:,.2f}")
                stop_diff = ((args.stop_price - current_price) / current_price) * 100
                print(f"   Stop vs Current: {stop_diff:+.2f}%")
            
            order = stop_limit_orders.place_stop_loss_order(
                args.symbol, args.quantity, args.stop_price, args.limit_price, args.side
            )
            
            display_order_details(order)

        elif args.order_type == 'take-profit':
            print(f" Placing TAKE-PROFIT order...")
            print(f"   Symbol: {args.symbol.upper()}")
            print(f"   Side: {args.side.upper()}")
            print(f"   Quantity: {args.quantity}")
            print(f"   Stop Price: ${args.stop_price:,.2f}")
            print(f"   Limit Price: ${args.limit_price:,.2f}")
            
            stop_limit_orders = StopLimitOrders()
            
            # Show current market price for reference
            current_price = stop_limit_orders.get_current_price(args.symbol)
            if current_price:
                print(f"   Current Price: ${current_price:,.2f}")
                profit_diff = ((args.stop_price - current_price) / current_price) * 100
                print(f"   Profit Target: {profit_diff:+.2f}%")
            
            order = stop_limit_orders.place_take_profit_order(
                args.symbol, args.quantity, args.stop_price, args.limit_price, args.side
            )
            
            display_order_details(order)

        elif args.order_type == 'oco':
            print(f" Placing OCO (One-Cancels-Other) orders...")
            print(f"   Symbol: {args.symbol.upper()}")
            print(f"   Side: {args.side.upper()}")
            print(f"   Quantity: {args.quantity}")
            print(f"   Take-Profit: ${args.take_profit:,.2f}")
            print(f"   Stop-Loss: ${args.stop_loss:,.2f}")
            
            oco_orders = OCOOrders()
            
            # Show current market price for reference
            current_price = oco_orders.get_current_price(args.symbol)
            if current_price:
                print(f"   Current Price: ${current_price:,.2f}")
                tp_diff = ((args.take_profit - current_price) / current_price) * 100
                sl_diff = ((args.stop_loss - current_price) / current_price) * 100
                print(f"   Take-Profit vs Current: {tp_diff:+.2f}%")
                print(f"   Stop-Loss vs Current: {sl_diff:+.2f}%")
            
            oco_result = oco_orders.place_oco_order(
                args.symbol, args.quantity, args.take_profit, args.stop_loss, args.side
            )
            
            display_oco_details(oco_result)
            
            if oco_result:
                print(f"\n Use 'python monitor_oco.py --oco-id {oco_result['oco_id']}' to monitor this OCO order")

        elif args.order_type == 'twap':
            print(f" Initiating TWAP {args.side.upper()} order...")
            print(f"   Symbol: {args.symbol.upper()}")
            print(f"   Total Quantity: {args.total_quantity}")
            print(f"   Duration: {args.duration} minutes")
            print(f"   Chunks: {args.chunks if args.chunks else args.duration}")
            print(f"   Order Type: {args.order_type.upper()}")
            
            twap_orders = TWAPOrders()
            
            # Show current market price for reference
            current_price = twap_orders.get_current_price(args.symbol)
            if current_price:
                print(f"   Current Price: ${current_price:,.2f}")
                estimated_value = current_price * args.total_quantity
                print(f"   Estimated Total Value: ${estimated_value:,.2f}")
            
            twap_config = twap_orders.place_twap_order(
                args.symbol, args.total_quantity, args.side, 
                args.duration, args.chunks, args.order_type
            )
            
            display_twap_details(twap_config)
            
            if twap_config:
                print(f"\n Use 'python monitor_twap.py --twap-id {twap_config['twap_id']}' to monitor this TWAP order")
        
        else:
            print(f" Unknown order type: {args.order_type}")
            return

        if args.order_type in ['market', 'limit', 'stop-loss', 'take-profit']:
            logging.info(f"Successfully placed {args.order_type} order")
        else:
            logging.info(f"Successfully initiated {args.order_type} strategy")

        if order:
            logging.info(f"Successfully placed {args.order_type} {args.side} order: {order}")
        else:
            logging.error("Order placement failed. See logs for details.")

    except KeyboardInterrupt:
        print("\n Operation cancelled by user")
        logging.info("Operation cancelled by user")
    except Exception as e:
        logging.error(f"An unexpected error occurred in main: {e}", exc_info=True)
        print(f" An unexpected error occurred: {e}")
        print("Check bot.log for detailed error information.")


if __name__ == "__main__":
    setup_logging()
    print("=" * 80)
    print(" PrimeTrade.ai Advanced Binance Futures Trading Bot")
    print("=" * 80)
    print(" Available Order Types:")
    print("   • Basic: market, limit")
    print("   • Advanced: stop-loss, take-profit, oco, twap")
    print("=" * 80)
    main()

# def main():
#     print("Hello from prime-trade!")

#     # Example usage
#     print(market_orders.place_buy_order("BTCUSDT", 0.001))
#     print(market_orders.place_sell_order("BTCUSDT", 0.001))

# if __name__ == "__main__":
#     main()
