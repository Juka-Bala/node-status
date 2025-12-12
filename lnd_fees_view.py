import sqlite3
import datetime
import os
from pathlib import Path

# Por padrão, usa um arquivo lnd_fees.sqlite na mesma pasta do script.
# Opcionalmente, pode ser sobrescrito pela variável de ambiente LND_FEES_DB.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("LND_FEES_DB", str(BASE_DIR / "lnd_fees.sqlite"))


def connect():
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)


def fetch_daily_latest():
    with connect() as conn:
        row = conn.execute(
            """
            SELECT date, forward_fees_sat, rebalance_fees_sat, net_profit_sat
            FROM daily_fees
            WHERE date = (SELECT MAX(date) FROM daily_fees)
            """
        ).fetchone()
    return row


def fetch_month_summary():
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT substr(date, 1, 7) AS ym,
                   SUM(forward_fees_sat),
                   SUM(rebalance_fees_sat),
                   SUM(net_profit_sat)
            FROM daily_fees
            GROUP BY ym
            ORDER BY ym DESC
            LIMIT 6
            """
        ).fetchall()
    return rows


def fetch_ytd():
    year = str(datetime.date.today().year)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT SUM(forward_fees_sat),
                   SUM(rebalance_fees_sat),
                   SUM(net_profit_sat)
            FROM daily_fees
            WHERE date LIKE ? || '-%%'
            """,
            (year,),
        ).fetchone()
    return row
