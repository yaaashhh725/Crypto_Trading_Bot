import logging

def validate_positive_number(value, name="value"):
    """
    Validates that a given value is a positive number.
    
    Args:
        value: The number to validate.
        name (str): The name of the value being validated (e.g., 'quantity', 'price').
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(value, (int, float)) or value <= 0:
        logging.error(f"Invalid {name}: {value}. It must be a positive number.")
        print(f"Error: Invalid {name}. Please provide a positive number.")
        return False
    return True

def validate_symbol(client, symbol):
    """
    Validates that the symbol is a valid and tradable futures symbol by checking with the API.
    
    Args:
        client: The Binance client instance.
        symbol (str): The symbol to validate (e.g., 'BTCUSDT').
        
    Returns:
        bool: True if the symbol is valid and tradable, False otherwise.
    """
    try:
        logging.info(f"Validating symbol: {symbol.upper()}")
        exchange_info = client.futures_exchange_info()
        valid_symbols = {s['symbol'] for s in exchange_info['symbols']}

        if symbol.upper() not in valid_symbols:
            logging.error(f"Invalid symbol: {symbol}. It does not exist on Binance Futures.")
            print(f"Error: The symbol '{symbol}' is not a valid futures symbol.")
            return False
        
        # Additionally, check if the symbol is actively trading
        for s_info in exchange_info['symbols']:
            if s_info['symbol'] == symbol.upper():
                if s_info['status'] != 'TRADING':
                    logging.error(f"Symbol {symbol} is not currently trading. Its status is {s_info['status']}.")
                    print(f"Error: The symbol '{symbol}' is not available for trading right now.")
                    return False
        
        logging.info(f"Symbol {symbol} is valid and tradable.")
        return True
    except Exception as e:
        logging.error(f"An error occurred while validating the symbol {symbol}: {e}", exc_info=True)
        print("An error occurred while trying to validate the symbol with Binance. Please check your connection and API keys.")
        return False
