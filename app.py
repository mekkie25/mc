import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for
import database
import portal_bridge
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json

from matrix import start_bot

app = Flask(__name__)
database.init_db()

# Start trading bot in background thread
def run_bot():
    try:
        start_bot()
    except Exception as e:
        print(f"Bot Runtime Error: {e}", flush=True)

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

SPREADSHEET_ID = "1tUnFGfr-syYknl0-_dwqJEEwChbinnCxVT-xHm6Nol0"

def fetch_sheet_trades():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        if "GOOGLE_CREDENTIALS_JSON" in os.environ:
            creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
            creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        elif os.path.exists("google_credentials.json"):
            creds = Credentials.from_service_account_file("google_credentials.json", scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else:
            print("Sheet Fetch Error: No credentials found.", flush=True)
            return []
        
        client = gspread.authorize(creds)
        doc = client.open_by_key(SPREADSHEET_ID)
        
        month_name = datetime.now().strftime("%B %Y")
        try:
            sheet = doc.worksheet(month_name)
        except Exception:
            sheet = doc.sheet1

        rows = sheet.get_all_values()
        
        header_idx = -1
        for idx, row in enumerate(rows):
            if "Date" in row and "Net_Money_Profit" in row:
                header_idx = idx
                break
        
        if header_idx == -1:
            print("Sheet Fetch Error: Headers not found in sheet rows.", flush=True)
            return []
        
        headers = rows[header_idx]
        trade_rows = rows[header_idx+1:]
        
        records = []
        for r in trade_rows:
            if not any(r):
                continue
            record = {}
            for h_idx, h_name in enumerate(headers):
                if h_idx < len(r):
                    record[h_name] = r[h_idx]
                else:
                    record[h_name] = ""
            records.append(record)
        return records
    except Exception as e:
        print(f"Sheet Fetch Error Exception: {e}", flush=True)
        return []

@app.route('/')
def dashboard():
    control = database.get_control_settings()
    records = fetch_sheet_trades()

    # Live balance/equity comes from matrix.py's telemetry writes (portal_bridge),
    # not a broker terminal call — the bot trades through Deriv's WebSocket API,
    # so there's no local MT5/IG terminal for this process to query directly.
    portal_state = portal_bridge.read_portal_inputs() or {}
    live_equity = portal_state.get("live_equity", 0.0)
    currency_symbol = "$"  # Deriv ConfigManager.BASE_ACCOUNT_CURRENCY is USD; adjust if that changes

    total_pnl = 0.0
    winning_trades = 0

    for row in records:
        try:
            pnl = float(row.get('Net_Money_Profit', 0.0) or 0.0)
        except (ValueError, TypeError):
            pnl = 0.0

        total_pnl += pnl
        if pnl > 0:
            winning_trades += 1

    total_trades = len(records)
    win_rate = round((winning_trades / total_trades * 100), 1) if total_trades > 0 else 0.0

    stats = {
        "pnl": round(total_pnl, 2),
        "win_rate": win_rate,
        "total_trades": total_trades,
        "equity": live_equity,
        "currency_symbol": currency_symbol
    }

    return render_template('index.html', control=control, stats=stats, trades=records)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    bot_enabled = 'bot_enabled' in request.form
    risk_percent = float(request.form.get('risk_percent', 2.0))
    rr_ratio = float(request.form.get('rr_ratio', 2.0))
    max_daily_trades = int(request.form.get('max_daily_trades', 2))
    lot_size = float(request.form.get('lot_size', 0.10))
    daily_target = float(request.form.get('daily_target', 50.0))
    weekly_target = float(request.form.get('weekly_target', 250.0))
    max_daily_loss = float(request.form.get('max_daily_loss', 20.0))
    max_weekly_loss = float(request.form.get('max_weekly_loss', 100.0))
    
    database.update_control_settings(
        bot_enabled, risk_percent, rr_ratio, max_daily_trades,
        lot_size, daily_target, weekly_target, max_daily_loss, max_weekly_loss
    )
    
    config_payload = {
        "bot_enabled": bot_enabled,
        "risk_percent": risk_percent,
        "rr_ratio": rr_ratio,
        "max_daily_trades": max_daily_trades,
        "lot_size": lot_size,
        "daily_target": daily_target,
        "weekly_target": weekly_target,
        "max_daily_loss": max_daily_loss,
        "max_weekly_loss": max_weekly_loss
    }
    # Merge rather than overwrite: portal_settings.json also carries the live
    # telemetry matrix.py writes (live_balance, live_equity, market_regime,
    # active_setup, ai_verdict). A plain overwrite here was wiping those out
    # every time someone touched a dashboard slider.
    existing = portal_bridge.read_portal_inputs() or {}
    existing.update(config_payload)
    with open("portal_settings.json", "w") as f:
        json.dump(existing, f, indent=4)

    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)