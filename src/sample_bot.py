from binance import Client
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_Key")
API_SECRET = os.getenv("Secret_Key")

client = Client(API_KEY, API_SECRET,testnet=True)
def get_account_info():
    try:
        account_info = client.get_account()
        return account_info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
print(get_account_info())