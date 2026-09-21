import sqlite3

DB_FILE = "trading_portal.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create control settings table with full risk and target controls
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS control_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_enabled BOOLEAN NOT NULL DEFAULT 1,
            risk_percent REAL NOT NULL DEFAULT 2.0,
            rr_ratio REAL NOT NULL DEFAULT 2.0,
            max_daily_trades INTEGER NOT NULL DEFAULT 2,
            lot_size REAL NOT NULL DEFAULT 0.10,
            daily_target REAL NOT NULL DEFAULT 50.0,
            weekly_target REAL NOT NULL DEFAULT 250.0,
            max_daily_loss REAL NOT NULL DEFAULT 20.0,
            max_weekly_loss REAL NOT NULL DEFAULT 100.0
        )
    ''')
    
    # Seed initial default settings row if empty
    cursor.execute('SELECT COUNT(*) FROM control_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO control_settings (
                bot_enabled, risk_percent, rr_ratio, max_daily_trades,
                lot_size, daily_target, weekly_target, max_daily_loss, max_weekly_loss
            ) VALUES (1, 2.0, 2.0, 2, 0.10, 50.0, 250.0, 20.0, 100.0)
        ''')
    else:
        # Schema migration check for existing databases
        cursor.execute("PRAGMA table_info(control_settings)")
        existing_cols = [col[1] for col in cursor.fetchall()]
        new_cols = {
            "lot_size": "REAL DEFAULT 0.10",
            "daily_target": "REAL DEFAULT 50.0",
            "weekly_target": "REAL DEFAULT 250.0",
            "max_daily_loss": "REAL DEFAULT 20.0",
            "max_weekly_loss": "REAL DEFAULT 100.0"
        }
        for col_name, col_type in new_cols.items():
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE control_settings ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()

def get_control_settings():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM control_settings ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "bot_enabled": True,
        "risk_percent": 2.0,
        "rr_ratio": 2.0,
        "max_daily_trades": 2,
        "lot_size": 0.10,
        "daily_target": 50.0,
        "weekly_target": 250.0,
        "max_daily_loss": 20.0,
        "max_weekly_loss": 100.0
    }

def update_control_settings(bot_enabled, risk_percent, rr_ratio, max_daily_trades, lot_size=0.10, daily_target=50.0, weekly_target=250.0, max_daily_loss=20.0, max_weekly_loss=100.0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE control_settings
        SET bot_enabled = ?,
            risk_percent = ?,
            rr_ratio = ?,
            max_daily_trades = ?,
            lot_size = ?,
            daily_target = ?,
            weekly_target = ?,
            max_daily_loss = ?,
            max_weekly_loss = ?
        WHERE id = (SELECT id FROM control_settings ORDER BY id DESC LIMIT 1)
    ''', (bot_enabled, risk_percent, rr_ratio, max_daily_trades, lot_size, daily_target, weekly_target, max_daily_loss, max_weekly_loss))
    conn.commit()
    conn.close()