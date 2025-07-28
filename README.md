
## Running the project

1. Clone the repository
`git clone https://github.com/yaaashhh725/Crypto_Trading_Bot.git`

2. Add your API keys
 - Get your API keys from  ` https://testnet.binancefuture.com/en/futures/BTCUSDT`
 - Create a file named .env
 - Add the API_key and Secret_Key to the file

3. Install dependencies
```bash
uv sync
```

4. Follow the below steps to run.

To open helpdesk
```bash
uv run main.py -h
```
OR
```bash
uv run main.py --help
```

---

To place market order

```bash
# To BUY
uv run main.py market --symbol BTCUSDT --side buy --quantity 0.001

# To SELL
uv run main.py market --symbol ETHUSDT --side sell --quantity 0.01
```

---


To place limit order

```bash
# To BUY
uv run main.py limit --symbol BTCUSDT --side buy --quantity 0.001 --price 50000

# To SELL
uv run main.py limit --symbol ETHUSDT --side sell --quantity 0.01 --price 3000
```

---

To place advanced orders:
- Stop-loss order
```bash
uv run main.py stop-loss --symbol BTCUSDT --quantity 0.001 --stop-price 29000 --limit-price 28900
```

---

- Take-profit order
```bash
uv run main.py take-profit --symbol BTCUSDT --quantity 0.001 --stop-price 31000 --limit-price 31100
```

---

- OCO order
```bash
uv run main.py oco --symbol BTCUSDT --quantity 0.001 --take-profit 31000 --stop-loss 29000
```

---

- TWAP order
```bash
uv run main.py twap --symbol BTCUSDT --side buy --total-quantity 0.01 --duration 10 --chunks 5
```