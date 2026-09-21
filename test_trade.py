import MetaTrader5 as mt5

if not mt5.initialize():
    print("❌ MT5 Initialization Failed")
    mt5.shutdown()
    exit()

account = mt5.account_info()
if account:
    print(f"✅ Connected to MT5 Account: {account.login}")
    print(f"💰 Account Equity: {account.currency} {account.equity:,.2f}")

symbol = "EURUSD"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None or not symbol_info.visible:
    mt5.symbol_select(symbol, True)

price = mt5.symbol_info_tick(symbol).ask
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": 0.01,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": price - 0.0020,
    "tp": price + 0.0040,
    "deviation": 20,
    "magic": 100001,
    "comment": "NEXUS Test Trade",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

result = mt5.order_send(request)
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"❌ Trade Execution Failed: {result.comment} (Code {result.retcode})")
else:
    print(f"🚀 TRADE EXECUTED SUCCESSFULLY! Order Ticket: {result.order}")

mt5.shutdown()