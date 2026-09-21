import MetaTrader5 as mt5

print("Connecting to the running MT5 application...")

# Initialize without any paths or credentials
# It will automatically find the active terminal on your desktop
if not mt5.initialize():
    print("Connection failed! Error:", mt5.last_error())
else:
    print("🎉 SUCCESS: Connected to MetaTrader 5!")
    
    account_info = mt5.account_info()
    if account_info is not None:
        print(f"Account ID: {account_info.login}")
        print(f"Balance: ${account_info.balance}")
    else:
        print("Connected, but couldn't fetch details.")
        
    mt5.shutdown()
